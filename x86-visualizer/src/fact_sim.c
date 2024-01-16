#include <panel.h>
#include <stdlib.h>
#include <string.h>

#define CALLER_RA 0xff
#define FACTORIAL_RA 0x1040
#define MEM_CELLS 20
#define N_INSTRUCTIONS 18
#define N_REGISTERS 5
#define UNINITIALIZED 0xfe

#define LABEL_COLS 7
#define BOX_ROWS 3
#define BOX_COLS 16

#define DIM 1
#define HIGHLIGHT 2

const long offsets[N_INSTRUCTIONS] = {
	0x1000,
	0x1004,
	0x1009,
	0x100f,
	0x1015,
	0x101e,
	0x1023,
	0x1028,
	0x102d,
	0x1034,
	0x1037,
	0x103b,
	0x1040,
	0x1044,
	0x1048,
	0x104d,
	0x1052,
	0x1056,
};

const char *instructions[N_INSTRUCTIONS] = {
	"subq  $0x18, %rsp",
	"movq  %rdi, 0x8(%rsp)",
	"cmpq  $0x0, 0x8(%rsp)",
	"jne   0x1023",
	"movq  $0x1, 0x10(%rsp)",
	"jmp   0x104d",
	"movq  0x8(%rsp), %rax",
	"movq  0x8(%rsp), %rcx",
	"subq  $0x1, %rcx",
	"movq  %rcx, %rdi",
	"movq  %rax, (%rsp)",
	"callq  _factorial",
	"movq  (%rsp), %rcx",
	"imulq %rax, %rcx",
	"movq  %rcx, 0x10(%rsp)",
	"movq  0x10(%rsp), %rax",
	"addq  $0x18, %rsp",
	"retq",
};

const char *mem_label = "STACK MEMORY";
const char *reg_label = "REGISTERS";
const char *ins_label = "INSTRUCTIONS";

const char *rip_annotation = "%%rip";
const char *rsp_annotation = "%%rsp";

int changed_mem = -1;
long memory[MEM_CELLS];

#define REG_RIP 0
#define REG_RSP 1
#define REG_RDI 2
#define REG_RAX 3
#define REG_RCX 4

// NOTE: %rsp is stored as an index into memory, rather than bytes
// (multiply it by 8 when displaying)
int changed_reg = -1;
long prev_rip = -1;
long rip, rsp, rdi, rax, rcx;

void step() {
	prev_rip = rip;

	switch (rip) {
		case 0x1000:
			rsp -= 3;

			changed_mem = -1;
			changed_reg = REG_RSP;

			rip = 0x1004;
			break;

		case 0x1004:
			memory[rsp + 1] = rdi;

			changed_mem = rsp + 1;
			changed_reg = -1;

			rip = 0x1009;
			break;

		case 0x1009:
			changed_mem = -1;
			changed_reg = -1;

			rip = 0x100f;
			break;

		case 0x100f:
			if (memory[rsp + 1] != 0) {
				rip = 0x1023;
			} else {
				rip = 0x1015;
			}

			changed_mem = -1;
			changed_reg = -1;

			break;

		case 0x1015:
			memory[rsp + 2] = 0x01;

			changed_mem = rsp + 2;
			changed_reg = -1;

			rip = 0x101e;
			break;

		case 0x101e:
			changed_mem = -1;
			changed_reg = -1;

			rip = 0x104d;
			break;

		case 0x1023:
			rax = memory[rsp + 1];

			changed_mem = -1;
			changed_reg = REG_RAX;

			rip = 0x1028;
			break;

		case 0x1028:
			rcx = memory[rsp + 1];

			changed_mem = -1;
			changed_reg = REG_RCX;

			rip = 0x102d;
			break;

		case 0x102d:
			rcx -= 0x01;

			changed_mem = -1;
			changed_reg = REG_RCX;

			rip = 0x1034;
			break;

		case 0x1034:
			rdi = rcx;

			changed_mem = -1;
			changed_reg = REG_RDI;

			rip = 0x1037;
			break;

		case 0x1037:
			memory[rsp] = rax;

			changed_mem = rsp;
			changed_reg = -1;

			rip = 0x103b;
			break;

		case 0x103b:
			// Push %rip to stack
			rsp -= 1;
			memory[rsp] = FACTORIAL_RA;

			changed_mem = rsp;
			changed_reg = REG_RSP;

			rip = 0x1000;
			break;

		case 0x1040:
			rcx = memory[rsp];

			changed_mem = -1;
			changed_reg = REG_RCX;

			rip = 0x1044;
			break;

		case 0x1044:
			rcx *= rax;

			changed_mem = -1;
			changed_reg = REG_RCX;

			rip = 0x1048;
			break;

		case 0x1048:
			memory[rsp + 2] = rcx;

			changed_mem = rsp + 2;
			changed_reg = -1;

			rip = 0x104d;
			break;

		case 0x104d:
			rax = memory[rsp + 2];

			changed_mem = -1;
			changed_reg = REG_RAX;

			rip = 0x1052;
			break;

		case 0x1052:
			rsp += 3;

			changed_mem = -1;
			changed_reg = REG_RSP;

			rip = 0x1056;
			break;

		case 0x1056:
			rip = memory[rsp];
			rsp += 1;

			changed_mem = -1;
			changed_reg = REG_RSP;

			break;

		default:
			fprintf(stderr, "unexpected %%rip = 0x%03lx\n", rip);
			break;
	}
}

void inner_box(WINDOW *w, int rows, int cols, int y0, int x0) {
	mvwhline(w, y0, x0, ACS_HLINE, cols);
	mvwhline(w, y0 + rows - 1, x0, ACS_HLINE, cols);
	mvwvline(w, y0, x0, ACS_VLINE, rows);
	mvwvline(w, y0, x0 + cols - 1, ACS_VLINE, rows);
	mvwaddch(w, y0, x0, ACS_ULCORNER);
	mvwaddch(w, y0, x0 + cols - 1, ACS_URCORNER);
	mvwaddch(w, y0 + rows - 1, x0, ACS_LLCORNER);
	mvwaddch(w, y0 + rows - 1, x0 + cols - 1, ACS_LRCORNER);
}

void reg_print(WINDOW *w, int offset, char *name, int reg, long value, int decimal) {
	inner_box(w, BOX_ROWS, BOX_COLS, 1 + BOX_ROWS * offset, LABEL_COLS);

	if (changed_reg == reg) {
		wattron(w, COLOR_PAIR(HIGHLIGHT));
	}
	mvwprintw(w, 2 + BOX_ROWS * offset, 2, "%%%s", name);
	int x = LABEL_COLS + (BOX_COLS - 4) / 2;
	if (reg == REG_RIP || reg == REG_RSP) {
		x--;
	}
	mvwprintw(w, 2 + BOX_ROWS * offset, x, "0x%02lx", value);
	if (decimal && value >= 10) {
		mvwprintw(w, 2 + BOX_ROWS * offset, LABEL_COLS + BOX_COLS + 1, "(%d)", value);
	}
	if (changed_reg == reg) {
		wattroff(w, COLOR_PAIR(HIGHLIGHT));
	}
}

const int spacing_mem_reg = 24;

int rows_reg, cols_reg;
int rows_ins, cols_ins;
int rows_mem, cols_mem;
int rows_total, cols_total;

int y0_mem, x0_mem;
int y0_reg, x0_reg;
int y0_ins, x0_ins;

WINDOW *w_memaddr, *w_mem, *w_rsp;
WINDOW *w_reg;
WINDOW *w_insaddr, *w_ins, *w_rip;

PANEL *p_memaddr, *p_mem, *p_rsp;
PANEL *p_reg;
PANEL *p_insaddr, *p_ins, *p_rip;

void init_layout() {
	int max_inslen = 0;
	for (int i = 0; i < N_INSTRUCTIONS; i++) {
		int inslen = strlen(instructions[i]);
		if (inslen > max_inslen) {
			max_inslen = inslen;
		}
	}

	rows_reg = BOX_ROWS * N_REGISTERS + 1;
	cols_reg = LABEL_COLS + BOX_COLS + 5;

	rows_ins = N_INSTRUCTIONS + 4;
	cols_ins = max_inslen + 4;

	rows_mem = 2 * MEM_CELLS + 2;
	cols_mem = BOX_COLS;

	rows_total = rows_mem;
	cols_total = cols_mem + cols_reg + spacing_mem_reg - LABEL_COLS;
}

void swap_panel(PANEL *p, WINDOW *w) {
	WINDOW *old = panel_window(p);
	replace_panel(p, w);
	delwin(old);
}

void do_layout(int replace) {
	y0_mem = (LINES - rows_total) / 2;
	x0_mem = (COLS - cols_total) / 2;

	y0_reg = y0_mem;
	x0_reg = x0_mem + cols_mem + spacing_mem_reg;

	y0_ins = y0_mem + rows_mem - rows_ins;
	x0_ins = x0_reg + LABEL_COLS + BOX_COLS - cols_ins;

	w_memaddr = newwin(rows_mem, LABEL_COLS, y0_mem, x0_mem - LABEL_COLS);
	w_mem = newwin(rows_mem, cols_mem, y0_mem, x0_mem);
	w_rsp = newwin(rows_mem, 2 + strlen(rsp_annotation), y0_mem, x0_mem + cols_mem + 1);

	w_reg = newwin(rows_reg, cols_reg, y0_reg, x0_reg);

	w_insaddr = newwin(rows_ins, LABEL_COLS, y0_ins, x0_ins - LABEL_COLS);
	w_ins = newwin(rows_ins, cols_ins, y0_ins, x0_ins);
	w_rip = newwin(rows_ins - 4, strlen(rip_annotation), y0_ins + 3, x0_ins + cols_ins + 1);

	if (replace) {
		swap_panel(p_memaddr, w_memaddr);
		swap_panel(p_mem, w_mem);
		swap_panel(p_rsp, w_rsp);

		swap_panel(p_reg, w_reg);

		swap_panel(p_insaddr, w_insaddr);
		swap_panel(p_ins, w_ins);
		swap_panel(p_rip, w_rip);
	} else {
		p_memaddr = new_panel(w_memaddr);
		p_mem = new_panel(w_mem);
		p_rsp = new_panel(w_rsp);

		p_reg = new_panel(w_reg);

		p_insaddr = new_panel(w_insaddr);
		p_ins = new_panel(w_ins);
		p_rip = new_panel(w_rip);
	}
}

short r_black, g_black, b_black;
short r_white, g_white, b_white;
short r_blue, g_blue, b_blue;

void init_color_hack() {
	color_content(COLOR_BLACK, &r_black, &g_black, &b_black);
	color_content(COLOR_WHITE, &r_white, &g_white, &b_white);
	color_content(COLOR_BLUE, &r_blue, &g_blue, &b_blue);

	init_color(COLOR_BLACK, 1000, 1000, 1000);
	init_color(COLOR_WHITE, 0, 0, 0);
	init_color(COLOR_BLUE, 800, 800, 800);

	init_pair(DIM, COLOR_BLUE, COLOR_BLACK);
	init_pair(HIGHLIGHT, COLOR_WHITE, COLOR_BLUE);
}

void restore_colors() {
	init_color(COLOR_BLACK, r_black, g_black, b_black);
	init_color(COLOR_WHITE, r_white, g_white, b_white);
	init_color(COLOR_BLUE, r_blue, g_blue, b_blue);
}

int main() {
	rdi = 4; // Calculate factorial(4)

	rip = 0x1000;
	rsp = MEM_CELLS - 1;
	for (int i = 0; i < rsp; i++) {
		memory[i] = UNINITIALIZED;
	}
	memory[rsp] = CALLER_RA;

	initscr();
	curs_set(0);
	noecho();
	keypad(stdscr, TRUE);
	raw();
	start_color();
	// For screen recording auto-animation
	// wtimeout(stdscr, 500);

	init_color_hack();
	init_layout();

	do_layout(FALSE);

	while (rip != CALLER_RA) {
		mvwprintw(w_reg, 0, LABEL_COLS + BOX_COLS - strlen(reg_label), reg_label);
		reg_print(w_reg, 0, "rip", REG_RIP, rip, FALSE);
		reg_print(w_reg, 1, "rsp", REG_RSP, 0xff00 + 8 * rsp, FALSE);
		reg_print(w_reg, 2, "rdi", REG_RDI, rdi, TRUE);
		reg_print(w_reg, 3, "rax", REG_RAX, rax, TRUE);
		reg_print(w_reg, 4, "rcx", REG_RCX, rcx, TRUE);

		// %rip label
		int idx_rip = -1;
		for (int i = 0; i < N_INSTRUCTIONS; i++) {
			if (rip == offsets[i]) {
				idx_rip = i;
			}
		}
		mvwprintw(w_rip, idx_rip, 0, rip_annotation, rip);

		// Instruction addresses
		for (int i = 0; i < N_INSTRUCTIONS; i++) {
			mvwprintw(w_insaddr, 3 + i, 0, "0x%04x", offsets[i]);
		}

		// Instructions
		mvwprintw(w_ins, 0, cols_ins - strlen(ins_label), ins_label);
		mvwprintw(w_ins, 2, 2, "_factorial:");
		inner_box(w_ins, rows_ins - 1, cols_ins, 1, 0);
		for (int i = 0; i < N_INSTRUCTIONS; i++) {
			int y = 3 + i;
			int x = 2;
			if (prev_rip == offsets[i]) {
				wattron(w_ins, COLOR_PAIR(HIGHLIGHT));
				mvwprintw(w_ins, y, x, "%s", instructions[i]);
				wattroff(w_ins, COLOR_PAIR(HIGHLIGHT));
			} else if (rip == offsets[i]) {
				wattron(w_ins, A_STANDOUT);
				mvwprintw(w_ins, y, x, "%s", instructions[i]);
				wattroff(w_ins, A_STANDOUT);
			} else {
				mvwprintw(w_ins, y, x, "%s", instructions[i]);
			}
		}

		// %rsp label
		if (changed_reg == REG_RSP) {
			wattron(w_rsp, COLOR_PAIR(HIGHLIGHT));
		}
		int idx_rsp = MEM_CELLS - 1 - rsp;
		mvwprintw(w_rsp, 2 + 2 * idx_rsp, 3, rsp_annotation);
		if (changed_reg == REG_RSP) {
			wattroff(w_rsp, COLOR_PAIR(HIGHLIGHT));
		}

		// Stack frame bounds
		for (int cell = 0; cell < MEM_CELLS; cell++) {
			int idx = MEM_CELLS - 1 - cell;
			if (idx >= rsp) {
				if (memory[idx] == CALLER_RA) {
					mvwaddch(w_rsp, 1 + 2 * cell, 0, ACS_HLINE);
					mvwaddch(w_rsp, 1 + 2 * cell, 1, ACS_URCORNER);
				} else if (memory[idx] == FACTORIAL_RA) {
					mvwaddch(w_rsp, 1 + 2 * cell, 0, ACS_HLINE);
					mvwaddch(w_rsp, 1 + 2 * cell, 1, ACS_RTEE);
				}

				mvwaddch(w_rsp, 2 + 2 * cell, 1, ACS_VLINE);

				if (idx == rsp || (idx > 0 && memory[idx - 1] == FACTORIAL_RA)) {
					mvwaddch(w_rsp, 3 + 2 * cell, 0, ACS_HLINE);
					mvwaddch(w_rsp, 3 + 2 * cell, 1, ACS_LRCORNER);
				} else {
					mvwaddch(w_rsp, 3 + 2 * cell, 0, ' ');
					mvwaddch(w_rsp, 3 + 2 * cell, 1, ACS_VLINE);
				}
			} else {
				mvwprintw(w_rsp, 2 + 2 * cell, 0, "  ");
				mvwprintw(w_rsp, 3 + 2 * cell, 0, "  ");
			}
		}

		// Memory cells
		inner_box(w_mem, rows_mem - 1, cols_mem, 1, 0);
		for (int cell = 1; cell < MEM_CELLS; cell++) {
			int y = 1 + 2 * cell;
			mvwaddch(w_mem, y, 0, ACS_LTEE);
			mvwhline(w_mem, y, 1, ACS_HLINE, cols_mem - 2);
			mvwaddch(w_mem, y, cols_mem - 1, ACS_RTEE);
		}

		// Memory addresses
		mvwprintw(w_mem, 0, BOX_COLS - strlen(mem_label), mem_label);
		for (int cell = 0; cell < MEM_CELLS; cell++) {
			int idx = MEM_CELLS - 1 - cell;
			if (idx == changed_mem) {
				wattron(w_memaddr, COLOR_PAIR(HIGHLIGHT));
			}
			mvwprintw(w_memaddr, 2 + 2 * cell, 0, "0x%04x", 0xff00 + 8 * idx);
			if (idx == changed_mem) {
				wattroff(w_memaddr, COLOR_PAIR(HIGHLIGHT));
			}
		}

		// Memory contents
		for (int cell = 0; cell < MEM_CELLS; cell++) {
			int idx = MEM_CELLS - 1 - cell;
			if (idx < rsp) {
				wattron(w_mem, COLOR_PAIR(DIM));
			}
			if (idx == changed_mem) {
				wattron(w_mem, COLOR_PAIR(HIGHLIGHT));
			}

			int y = 2 + 2 * cell;
			int x = cols_mem / 2 - 2;
			if (memory[idx] == UNINITIALIZED) {
				mvwprintw(w_mem, y, x, "    ", memory[idx]);
			} else if (memory[idx] == CALLER_RA) {
				mvwprintw(w_mem, y, x - 2, "(caller)", memory[idx]);
			} else if (memory[idx] > 0xff) {
				mvwprintw(w_mem, y, x - 1, "0x%04x", memory[idx]);
			} else {
				mvwprintw(w_mem, y, x, "0x%02x", memory[idx]);
			} 

			if (idx < rsp) {
				wattroff(w_mem, COLOR_PAIR(DIM));
			}
			if (idx == changed_mem) {
				wattroff(w_mem, COLOR_PAIR(HIGHLIGHT));
			}
		}

		update_panels();
		doupdate();

		int c = getch();
		switch (c) {
			case KEY_RESIZE:
				do_layout(TRUE);
				break;

			case 'q':
			case 'c' & 0x1f:
				restore_colors();
				endwin();
				exit(0);
				break;

			case ERR:
			case 10:
				// Clear annotations (only things that won't be redrawn)
				mvwaddch(w_rip, idx_rip, 0, '\n');
				mvwaddch(w_rsp, 2 + 2 * idx_rsp, 0, '\n');
				step();
				break;
		}
	}

	restore_colors();
	endwin();
}
