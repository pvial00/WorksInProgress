#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <utility>
#include <ctime>
using namespace std;
vector< vector< vector<int> > > sbox;

vector< vector< vector<int> > > gen_cube (int depth, int width, int length) {
    int z;
    int y;
    int x;
    int mod;
    int shift;
    vector< vector< vector<int> > > sbox;
    for (z=0; z != depth; z++) {
        vector< vector<int> > section_list;
        for (y=0; y != width; y++) {
            vector<int> alphabet;
            for (x=0; x != length; x++) {
                alphabet.push_back(x);
            }
            for (mod=0; mod != y; mod++) {
                shift = alphabet[0];
		alphabet.erase(alphabet.begin()+0);
                alphabet.push_back(shift);
                shift = alphabet[2];
                alphabet.erase(alphabet.begin()+2);
                alphabet.push_back(shift);
            }
            section_list.push_back(alphabet);
        }
        sbox.push_back(section_list);
    }
    return sbox;
}

vector< vector< vector<int> > > key_cube (vector< vector< vector<int> > > sbox, string key) {
    int z;
    int x;
    int y;
    int k;
    int chr;
    int shuffle;
    int key_sub;
    for (z=0; z != sbox.size(); z++) {
        vector< vector<int> > section;
        section = sbox[z];
        for (k=0; k != sizeof(key); k++) {
            chr = key[k];
            for (x=0; x != section.size(); x++) {
                vector<int> alphabet;
                alphabet = section[x];
                key_sub = alphabet[chr];
                alphabet.push_back(key_sub);
                for (y=0; y != chr; y++) {
                    if (y % 2 == 0) {
                        shuffle = alphabet[0];
                        alphabet.erase(alphabet.begin()+0);
                        alphabet.push_back(shuffle);
                        shuffle = alphabet[2];
                        alphabet.erase(alphabet.begin()+2);
                        alphabet.push_back(shuffle);
                    }
                }
            }
        }
    }
    return sbox;
}

string key_scheduler (string key) {
    int x;
    string sub_key;
    int sized_pos;
    int sub;
    string byte;
    for (x=0; x != sizeof(key); x++) {
	    sized_pos = key[x] % 3;
            sub = sbox[sized_pos][sized_pos][key[x]];
	    sbox[sized_pos][sized_pos].erase(sbox[sized_pos][sized_pos].begin()+key[x]);
            sbox[sized_pos][sized_pos].push_back(sub);
	    byte = sub;
	    sub_key.append(byte);
    return sub_key;

    }
}

int morph_cube (int counter, string sub_key) {
    int mod_value;
    vector< vector<int> >  section_shift ;
    mod_value = counter % 256;
    for (vector< vector<int> > section: sbox) {
	for (char key_element : sub_key) {
            for (vector<int> alphabet : section) {
		    swap(alphabet[mod_value], alphabet[key_element]);
        section_shift = sbox[(key_element % 3)];
	sbox.erase(sbox.begin()+(key_element % 3));
	sbox.push_back(section_shift);
            }
	}
    }
}

string encrypt (string data, string sub_key) {
    int ctr;
    int sub;
    int sub_pos;
    int shift;
    string byte;
    string cipher_text;
    for (ctr=0; ctr < data.length(); ctr++) {
        sub = data[ctr];
	for (vector< vector<int> > section: sbox) {
	    for (vector<int> alphabet : section) {
                sub_pos = sub;
		sub = alphabet[sub_pos];
		shift = alphabet[0];
		alphabet.erase(alphabet.begin()+0);
		alphabet.push_back(shift);
		
	    }
	}
	sub_key = key_scheduler(sub_key);
	morph_cube(ctr, sub_key);
	byte = sub;
	cipher_text.append(byte);
    }
    return cipher_text;
}

string decrypt (string data, string sub_key) {
    int ctr;
    int sub;
    int sub_pos;
    int shift;
    string byte;
    string cipher_text;
    std::reverse(sbox.begin(), sbox.end());
    for (ctr=0; ctr < data.length(); ctr++) {
        sub = data[ctr];
	for (vector< vector<int> > section: sbox) {
	    for (vector<int> alphabet : section) {
		sub = find(alphabet.begin(), alphabet.end(), sub) - alphabet.begin();
		shift = alphabet[0];
		alphabet.erase(alphabet.begin()+0);
		alphabet.push_back(shift);
	    }
	}
	sub_key = key_scheduler(sub_key);
	morph_cube(ctr, sub_key);
	byte = sub;
	cipher_text.append(byte);
    }
    return cipher_text;
}

int main(int argc, char** argv) {
    cout << "Test\n";
    ifstream infile;
    ofstream outfile;
    string mode;
    string data;
    string in;
    string out;
    string key;
    string b;
    mode = argv[1];
    in = argv[2];
    out = argv[3];
    key = argv[4];
    infile.open(in);
    while (infile >> b) {
        data = data + b;
    }
    infile.close();
    string c;
    clock_t begin = clock();
    cout << mode;
    if (mode == "encrypt") {
     	sbox = gen_cube(3, 3, 256);
    	sbox = key_cube(sbox, key);
    	c = encrypt(data, key);
    }
    else if (mode == "decrypt") {
     	sbox = gen_cube(3, 3, 256);
    	sbox = key_cube(sbox, key);
    	c = decrypt(data, key);
    }
    clock_t end = clock();
    cout << data.length() / (double(end - begin));
    outfile.open(out);
    outfile << c;
    outfile.close();
}
