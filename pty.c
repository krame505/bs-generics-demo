#define _XOPEN_SOURCE 500

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>

static int createPty() {
  int ptm = open("/dev/ptmx", O_RDWR);

  // Set nonblocking read
  int flags = fcntl(ptm, F_GETFL, 0);
  fcntl(ptm, F_SETFL, flags | O_NONBLOCK);

  // Set raw mode
  struct termios ptm_attr;
  tcgetattr(ptm,&ptm_attr);
  ptm_attr.c_lflag &= (~(ICANON|ECHO));
  ptm_attr.c_cc[VTIME] = 0;
  ptm_attr.c_cc[VMIN] = 1;
  tcsetattr(ptm,TCSANOW,&ptm_attr);

  grantpt(ptm);
  unlockpt(ptm);

  return ptm;
}

static bool initialized = false;
static int clientFD, simFD;
static pid_t simAppPID;
static void init(void) {
  if (!initialized) {
    clientFD = createPty();
    simFD = createPty();
    printf("Initialized simulated serial device at %s\n", ptsname(clientFD));

    simAppPID = fork();
    if (simAppPID == 0) {
      execlp("python3", "python3", "simapp.py", ptsname(simFD), NULL);
    }

    initialized = true;
  }
}

static void cleanup(void) {
  if (initialized) {
    kill(simAppPID, SIGTERM);
    waitpid(simAppPID, NULL, 0);
    close(clientFD);
    close(simFD);
    initialized = false;
  }
}

unsigned rxClient(void) {
  init();
  char c;
  if (read(clientFD, &c, 1) > 0) {
    return c & (unsigned)0xff;
  } else if (errno == EAGAIN) {
    // No data to read, do nothing
  } else if (errno == EIO) {
    // Connection was closed
    printf("Client app connection closed, exiting\n");
    cleanup();
    exit(0);
  } else {
    perror("Client PTY read error");
  }
  return -1;
}

void txClient(unsigned byte) {
  init();
  char c = byte;
  if (write(clientFD, &c, 1) != 1) {
    perror("Client PTY write error");
  }
}

unsigned rxSim(void) {
  init();
  char c;
  if (read(simFD, &c, 1) > 0) {
    return c & (unsigned)0xff;
  } else if (errno == EAGAIN) {
    // No data to read, do nothing
  } else if (errno == EIO) {
    // Connection was closed
    printf("Simulator app connection closed, exiting\n");
    cleanup();
    exit(0);
  } else {
    perror("Sim PTY read error");
  }
  return -1;
}

void txSim(unsigned byte) {
  init();
  char c = byte;
  if (write(simFD, &c, 1) != 1) {
    perror("Sim PTY write error");
  }
}

