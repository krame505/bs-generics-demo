#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

static FILE *tty = NULL;
static void init(void) {
  if (!tty) {
    tty = fopen("ttySim", "rb+");
  }
}

unsigned rxData(void) {
  init();
  int c = getc(tty);
  if (c != -1) {
    printf("rx %x\n", c);
  }
  return c;
}

void txData(unsigned byte) {
  init();
  putc(byte & 0xff, tty);
}
