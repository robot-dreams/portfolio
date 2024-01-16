#include <stdio.h>

long factorial(long n) {
	if (n == 0) {
		return 1;
	} else {
		return n * factorial(n - 1);
	}
}

int main() {
	printf("%ld\n", factorial(4));
}
