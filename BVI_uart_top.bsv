// BVI Wrapper created by: transactor generator on: Wed Jul  8 15:52:54 EDT 2020

import Connectable::*;
import Clocks::*;


(* always_ready, always_enabled *)
interface BVI_uart_top_IFC;
  (*prefix=""*) method Action 	        cts_pad_i ((*port="cts_pad_i"*) Bit#(1) x);
  (*prefix=""*) method Action 	        dcd_pad_i ((*port="dcd_pad_i"*) Bit#(1) x);
  (*prefix=""*) method Action 	        dsr_pad_i ((*port="dsr_pad_i"*) Bit#(1) x);
  (*result="dtr_pad_o"*) method Bit#(1) dtr_pad_o ();
  (*result="int_o"*) method Bit#(1) 	int_o ();
  (*prefix=""*) method Action 	        ri_pad_i ((*port="ri_pad_i"*) Bit#(1) x);
  (*result="rts_pad_o"*) method Bit#(1) rts_pad_o ();
  (*prefix=""*) method Action 	        srx_pad_i ((*port="srx_pad_i"*) Bit#(1) x);
  (*result="stx_pad_o"*) method Bit#(1) stx_pad_o ();

  (*result="wb_ack_o"*) method Bit#(1) 	wb_ack_o ();
  (*prefix=""*) method Action 	        wb_adr_i ((*port="wb_adr_i"*) Bit#(3) x);
  (*prefix=""*) method Action 	        wb_cyc_i ((*port="wb_cyc_i"*) Bit#(1) x);
  (*prefix=""*) method Action 	        wb_dat_i ((*port="wb_dat_i"*) Bit#(8) x);
  (*result="wb_dat_o"*) method Bit#(8)  wb_dat_o ();
  (*prefix=""*) method Action    	wb_sel_i ((*port="wb_sel_i"*) Bit#(1) x);
  (*prefix=""*) method Action 	        wb_stb_i ((*port="wb_stb_i"*) Bit#(1) x);
  (*prefix=""*) method Action 	        wb_we_i ((*port="wb_we_i"*) Bit#(1) x);
endinterface : BVI_uart_top_IFC

import "BVI" uart_top =
module mkBVI_uart_top (BVI_uart_top_IFC);
  let rstn <- exposeCurrentReset();
  let rst  <- mkResetInverter(rstn);
  default_clock (wb_clk_i, (*unused*)GATE);
  default_reset (wb_rst_i) = rst;

  parameter uart_addr_width = 3;
  parameter uart_data_width = 8;

  method /*Action*/ cts_pad_i (cts_pad_i) enable((*inhigh*) u0001);
  method /*Action*/ dcd_pad_i (dcd_pad_i) enable((*inhigh*) u0002);
  method /*Action*/ dsr_pad_i (dsr_pad_i) enable((*inhigh*) u0003);
  method /*Value*/ dtr_pad_o dtr_pad_o ();
  method /*Action*/ ri_pad_i (ri_pad_i) enable((*inhigh*) u0004);
  method /*Value*/ rts_pad_o rts_pad_o ();
  method /*Action*/ srx_pad_i (srx_pad_i) enable((*inhigh*) u0005);
  method /*Value*/ stx_pad_o stx_pad_o ();

  method /*Value*/ int_o int_o ();

  method /*Value*/ wb_ack_o wb_ack_o ();
  method /*Action*/ wb_adr_i (wb_adr_i) enable((*inhigh*) u0006);
  method /*Action*/ wb_cyc_i (wb_cyc_i) enable((*inhigh*) u0007);
  method /*Action*/ wb_dat_i (wb_dat_i) enable((*inhigh*) u0008);
  method /*Value*/ wb_dat_o wb_dat_o ();
  method /*Action*/ wb_sel_i (wb_sel_i) enable((*inhigh*) u0009);
  method /*Action*/ wb_stb_i (wb_stb_i) enable((*inhigh*) u0010);
  method /*Action*/ wb_we_i (wb_we_i) enable((*inhigh*) u0011);

  // Schedule for methods with clock: wb_clk_i
  schedule (dtr_pad_o,int_o,rts_pad_o,stx_pad_o,wb_ack_o,wb_dat_o) CF (dtr_pad_o,int_o,rts_pad_o,stx_pad_o,wb_ack_o,wb_dat_o);
  schedule (dtr_pad_o,int_o,rts_pad_o,stx_pad_o,wb_ack_o,wb_dat_o) CF (cts_pad_i,dcd_pad_i,dsr_pad_i,ri_pad_i,srx_pad_i,wb_adr_i,wb_cyc_i,wb_dat_i,wb_sel_i,wb_stb_i,wb_we_i);
  schedule cts_pad_i C cts_pad_i;
  schedule cts_pad_i CF (dcd_pad_i,dsr_pad_i,ri_pad_i,srx_pad_i,wb_adr_i,wb_cyc_i,wb_dat_i,wb_sel_i,wb_stb_i,wb_we_i);
  schedule dcd_pad_i C dcd_pad_i;
  schedule dcd_pad_i CF (dsr_pad_i,ri_pad_i,srx_pad_i,wb_adr_i,wb_cyc_i,wb_dat_i,wb_sel_i,wb_stb_i,wb_we_i);
  schedule dsr_pad_i C dsr_pad_i;
  schedule dsr_pad_i CF (ri_pad_i,srx_pad_i,wb_adr_i,wb_cyc_i,wb_dat_i,wb_sel_i,wb_stb_i,wb_we_i);
  schedule ri_pad_i C ri_pad_i;
  schedule ri_pad_i CF (srx_pad_i,wb_adr_i,wb_cyc_i,wb_dat_i,wb_sel_i,wb_stb_i,wb_we_i);
  schedule srx_pad_i C srx_pad_i;
  schedule srx_pad_i CF (wb_adr_i,wb_cyc_i,wb_dat_i,wb_sel_i,wb_stb_i,wb_we_i);
  schedule wb_adr_i C wb_adr_i;
  schedule wb_adr_i CF (wb_cyc_i,wb_dat_i,wb_sel_i,wb_stb_i,wb_we_i);
  schedule wb_cyc_i C wb_cyc_i;
  schedule wb_cyc_i CF (wb_dat_i,wb_sel_i,wb_stb_i,wb_we_i);
  schedule wb_dat_i C wb_dat_i;
  schedule wb_dat_i CF (wb_sel_i,wb_stb_i,wb_we_i);
  schedule wb_sel_i C wb_sel_i;
  schedule wb_sel_i CF (wb_stb_i,wb_we_i);
  schedule wb_stb_i C wb_stb_i;
  schedule wb_stb_i CF (wb_we_i);
  schedule wb_we_i C wb_we_i;
endmodule: mkBVI_uart_top
