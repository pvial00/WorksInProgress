#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
	FILE *infile, *outfile;
	int x, ch, kryptc;
	char buffer[32768];
	char *key, *in, *out;
	in = argv[1];
	out = argv[2];
	key = argv[3];
	
	if (argc != 4)
	{
		printf("usage: krypto <infile> <outfile> <key>\n");
	}
	else
	{
		infile = fopen("infile", "r");
		fseek(infile, 0, SEEK_END);
        	long fsize = ftell(infile);
        	fseek(infile, 0, SEEK_SET);
		outfile = fopen("outfile", "w");
		while ((ch = fgetc(infile)) != EOF)
		{
			for (x = 0; x < sizeof(key); x++)
			{
				kryptc = ch ^ key[x];
			}
			fputc(kryptc, outfile);
		}
	
		fclose(infile);
		fclose(outfile);
	}
}
