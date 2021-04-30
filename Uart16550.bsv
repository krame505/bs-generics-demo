package Uart16550;

import  Vector        :: *;
import  FIFOF         :: *;
import  GetPut        :: *;
import  ClientServer  :: *;
import  ConfigReg     :: *;
import  AXI4_Types    :: *;
import  Fabric_Defs   :: *;
import  GetPut_Aux    :: *;
import  Semi_FIFOF    :: *;
import Cur_Cycle      :: *;

import BVI_uart_top ::*;

// ----------------

function Action fail(Integer n);
   action
      $display ("%0d: ERROR: UART16550: fail %0d", cur_cycle, n);
      $finish(1);
   endaction
endfunction

// ----------------
// Split a bus address into (offset in UART, lsbs)

function Tuple3 #(Bit #(3), Bit #(3), Bit #(2)) split_addr (Fabric_Addr addr);
   // 4-byte stride
   Bit #(3)  msbs   = addr [7:5];
   Bit #(3)  offset = addr [4:2];
   Bit #(2)  lsbs   = addr [1:0];

   return tuple3 (msbs, offset, lsbs);
endfunction

// ----------------
// Type of fn_check_address's result

typedef union tagged {
   Bit#(3)   OK;
   AXI4_Resp Wrong;
   } Address_Check deriving (Eq, Bits);

// ----------------
(* always_ready, always_enabled *)
interface UART;
   method Action  cts_pad(Bit #(1) x);
   method Action  dcd_pad(Bit #(1) x);
   method Action  dsr_pad(Bit #(1) x);
   method Bit#(1) dtr_pad;
   method Action  ri_pad(Bit #(1) x);
   method Bit#(1) rts_pad;
   method Action  srx_pad(Bit #(1) x);
   method Bit#(1) stx_pad;
endinterface

interface UART_IFC;
   // Reset by default RST_N;

   // set_addr_map should be called after this module's reset
   method Action set_addr_map (Fabric_Addr addr_base, Fabric_Addr addr_lim);

   // Main Fabric Reqs/Rsps
   interface AXI4_Slave_IFC #(Wd_Id, Wd_Addr, Wd_Data, Wd_User) slave;

   // To external console
   interface UART uart;

   // Interrupt pending
   (* always_ready *)
   method Bool  intr;
endinterface

(*synthesize*)
module mkUart16550 (UART_IFC);
   Reg #(Fabric_Addr)  rg_addr_base <- mkRegU;
   Reg #(Fabric_Addr)  rg_addr_lim  <- mkRegU;

   // Communication registers:
   Reg #(Bit #(1))  rg_cyc   <- mkReg(0);
   Reg #(Bit #(1))  rg_stb   <- mkReg(0);
   Reg #(Bit #(1))  rg_we    <- mkReg(0);
   Reg #(Bit #(3))  rg_adr   <- mkReg(0);
   Reg #(Bit #(1))  rg_sel   <- mkReg(0);
   Reg #(Bit #(8))  rg_dat_i <- mkReg(0);

   Reg #(Bit #(1))  rg_ack[2]   <- mkCReg(2, 0);
   Reg #(Bit #(8))  rg_dat_o[2] <- mkCReg(2, 0);

   // FABRIC SIDE:

   AXI4_Slave_Xactor_IFC #(Wd_Id, Wd_Addr, Wd_Data, Wd_User) slave_xactor
      <- mkAXI4_Slave_Xactor;

   function ActionValue #(Address_Check) check_address (Fabric_Addr addr);
      actionvalue
	 let byte_addr = addr - rg_addr_base;
	 let { msbs, offset, lsbs } = split_addr (zeroExtend (byte_addr));

	 AXI4_Resp rresp      = axi4_resp_okay;

	 if (lsbs != 0) begin
	    $display ("%0d: ERROR: UART: misaligned addr", cur_cycle);
	    $display ("            ", fshow (addr));
	    rresp = axi4_resp_slverr;
	 end
	 else if (msbs != 0) begin
	    $display ("%0d: ERROR: UART.rl_process_rd_req: unrecognized addr", cur_cycle);
	    $display ("            ", fshow (addr));
	    rresp = axi4_resp_decerr;
	 end

	 if (rresp == axi4_resp_okay) return tagged OK offset;
	 else return tagged Wrong rresp;
      endactionvalue
   endfunction

   let idle =     (rg_stb == 0);
   let complete = (rg_ack[1] == 1);
   let ready    = idle || complete;

   Reg #(Maybe #(Bit #(8)))  rg_buffer   <- mkReg(Invalid);
   Reg #(Bool)               rg_shifting <- mkRegU;
   Reg #(Bit #(Wd_Id))       rg_id       <- mkRegU;
   Reg #(Bit #(Wd_User))     rg_user     <- mkRegU;
   Reg #(Bool)         crg_canRead[4] <- mkCReg(4, True);

   function Action send_data(Fabric_Data d);
      action
	 let rdr = AXI4_Rd_Data {rid:   rg_id,
				 rdata: d,
				 rresp: axi4_resp_okay,
				 rlast: True,
				 ruser: rg_user};
	 slave_xactor.i_rd_data.enq (rdr);
      endaction
   endfunction

   rule rl_clearBuffer (rg_buffer matches tagged Valid .x);
      Fabric_Data d = zeroExtend(x);
      if (rg_shifting) d = (d << 32);
      send_data(d);
      crg_canRead[0] <= True; // We know there won't be a send_data conflict
   endrule

   rule rl_complete_rd (rg_we == 0 && !isValid(rg_buffer) && complete);
      Fabric_Data d = zeroExtend(rg_dat_o[1]);
      if (rg_shifting) d = (d << 32);
      if (slave_xactor.i_rd_data.notFull()) begin
	 send_data(d);
	 crg_canRead[0] <= True;
      end
      else rg_buffer <= tagged Valid rg_dat_o[1];
   endrule

   rule rl_rd_req (crg_canRead[1] && ready);
      let rda <- pop_o (slave_xactor.o_rd_addr);
      let ca <-check_address(rda.araddr);
      case (ca) matches
	 tagged Wrong .e: begin
	    let rdr = AXI4_Rd_Data {rid:   rda.arid,
				    rdata: (?),
				    rresp: e,
				    rlast: True,
				    ruser: rda.aruser};
	    slave_xactor.i_rd_data.enq (rdr);
	 end
	 tagged OK .a: begin
	    // save values for response:
	    rg_id <= rda.arid;
	    rg_user <= rda.aruser;
	    rg_shifting <= (a[0] == 1);
	    // send values to 16550:
	    rg_adr <= a;
	    rg_sel <= 1;
	    rg_we  <= 0;
	    rg_cyc <= 1;
	    rg_stb <= 1;
	    // inhibit further reads till completed:
	    crg_canRead[1] <= False;
	 end
      endcase
   endrule

   (*preempts="rl_rd_req, rl_wr_req"*)
   rule rl_wr_req (ready);
      let wra <- pop_o (slave_xactor.o_wr_addr);
      let wrd <- pop_o (slave_xactor.o_wr_data);
      if (!wrd.wlast) fail(3); // don't do bursts
      let ca <-check_address(wra.awaddr);
      let wrr = AXI4_Wr_Resp {bid:   wra.awid,
			      bresp: axi4_resp_okay,
			      buser: wra.awuser};
      case (ca) matches
	 tagged Wrong .e: wrr.bresp = e;
	 tagged OK .a: begin
	    // shift data if necessary:
	    let dta = wrd.wdata;
	    let srb = wrd.wstrb;
	    if (a[0] == 1) begin
	       dta = dta >> 32;
	       srb = srb >> 4;
	    end
	    // send values to 16550:
	    rg_adr   <= a;
	    rg_dat_i <= truncate(dta);
	    rg_sel   <= truncate(srb);
	    rg_we    <= 1;
	    rg_cyc   <= 1;
	    rg_stb   <= 1;

	    Bit#(8) x = truncate(dta);
	    $write("%c", x);
	 end
      endcase
      // respond to SoC:
      slave_xactor.i_wr_resp.enq (wrr);
   endrule

   (*preempts="rl_rd_req, rl_cycle_end"*)
   (*preempts="rl_wr_req, rl_cycle_end"*)
   rule rl_cycle_end (complete);
      rg_stb <= 0; // no new transfer: idle
      rg_cyc <= 0;
   endrule

   // 16550 SIDE:

   let ifc <- mkBVI_uart_top;

   (*no_implicit_conditions, fire_when_enabled*) rule rl_cyc;   ifc.wb_cyc_i(rg_cyc);   endrule
   (*no_implicit_conditions, fire_when_enabled*) rule rl_stb;   ifc.wb_stb_i(rg_stb);   endrule
   (*no_implicit_conditions, fire_when_enabled*) rule rl_we;    ifc.wb_we_i (rg_we );   endrule
   (*no_implicit_conditions, fire_when_enabled*) rule rl_adr;   ifc.wb_adr_i(rg_adr);   endrule
   (*no_implicit_conditions, fire_when_enabled*) rule rl_sel;   ifc.wb_sel_i(rg_sel);   endrule
   (*no_implicit_conditions, fire_when_enabled*) rule rl_dat_i; ifc.wb_dat_i(rg_dat_i); endrule

   (*no_implicit_conditions, fire_when_enabled*) rule rl_ack;   rg_ack[0]   <= ifc.wb_ack_o; endrule
   (*no_implicit_conditions, fire_when_enabled*) rule rl_dat_o; rg_dat_o[0] <= ifc.wb_dat_o; endrule


   // Interface:

   // Main Fabric Reqs/Rsps
   interface  slave = slave_xactor.axi_side;

   method intr = unpack(ifc.int_o);

   interface UART uart;
      method cts_pad = ifc.cts_pad_i;
      method dcd_pad = ifc.dcd_pad_i;
      method dsr_pad = ifc.dsr_pad_i;
      method dtr_pad = ifc.dtr_pad_o;
      method ri_pad  = ifc.ri_pad_i;
      method rts_pad = ifc.rts_pad_o;
      method srx_pad = ifc.srx_pad_i;
      method stx_pad = ifc.stx_pad_o;
   endinterface


   // set_addr_map should be called after this module's reset
   method Action  set_addr_map (Fabric_Addr addr_base, Fabric_Addr addr_lim);
      if (addr_base [2:0] != 0)
	 $display ("%0d: WARNING: UART.set_addr_map: addr_base 0x%0h is not 8-Byte-aligned",
		   cur_cycle, addr_base);

      if (addr_lim [2:0] != 0)
	 $display ("%0d: WARNING: UART.set_addr_map: addr_lim 0x%0h is not 8-Byte-aligned",
		   cur_cycle, addr_lim);

      rg_addr_base <= addr_base;
      rg_addr_lim  <= addr_lim;
   endmethod
endmodule

endpackage
