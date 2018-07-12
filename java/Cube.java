import java.io.*;
import java.lang.*;
import java.util.*;

public class Cube {
   static int size_factor = 3;
   static int alphabet_size = 256;
   static ArrayList<ArrayList<ArrayList<Integer>>> state;
   public static ArrayList<ArrayList<ArrayList<Integer>>> gencube(int depth, int width, int length) {
      static ArrayList<ArrayList<ArrayList<Integer>>> state;
      for (int z = 0; z < depth; z++) {
          ArrayList<ArrayList<Integer>> section;
	  for (int y = 0; y < width; y++) {
              ArrayList<Integer> alphabet;
	      for (int x = 0; x < length; x++) {
	          alphabet.add(x);
	      }
	      for (int mod=0; mod < y; mod++) {
                 int shift;
		 shift = alphabet.get(0);
		 alphabet.remove(shift);
		 alphabet.add(shift);
		 shift = alphabet.get(2);
		 alphabet.remove(shift);
		 alphabet.add(127, shift);
	      }
	      section.add(alphabet);
	  }
	  state.add(section);
      }
      return state;
  }
  public static void key_cube(String key) {
     int key_sub;
     int sized_pos;
     int shuffle;
     for (int z; z < 3; z++) {
        for (int i = 0; i < key.length(); i++) {
	    for (int x = 0; x < state.get(z).size(); x++) {
	        key_sub = state.get(z).get(x).get(((int)key.charAt(i)));
		state.get(z).get(x).remove(key_sub);
		state.get(z).get(x).add(key_sub);
		for (int y = 0; y < (int)key.charAt(i); y++) {
                    if (y % 2 == 0) {
                        shuffle = state.get(z).get(x).get(0);
                        state.get(z).get(x).remove(shuffle);
			state.get(z).get(x).add(shuffle);
                        shuffle = state.get(z).get(x).get(2);
                        state.get(z).get(x).remove(shuffle);
			state.get(z).get(x).add(127, shuffle);
                     }
		}
	    }
        }
    }

    ArrayList<ArrayList<Integer>> section;
    for (int i = 0; i < key.length(); i++) {
       sized_pos = (int)key.charAt(i) % size_factor;
       for (int y = 0; y < (int)key.charAt(i); y++) {
          section = state.get(sized_pos);
	  state.remove(section);
	  state.add(section);
       }
   }
  }
   public static String key_scheduler (String key) {
       int sized_pos, sub;
       ArrayList<ArrayList<Integer>> section;
       ArrayList<Integer> sub_alpha;
       String sub_key;
       for (int i = 0; i < key.length(); i++) {
           sized_pos = (int)key.charAt(i) % size_factor;
	   sub = state.get(sized_pos).get(sized_pos).get((int)key.charAt(i));
	   state.get(sized_pos).get(sized_pos).remove(sub);
	   state.get(sized_pos).get(sized_pos).add(sub);
       }
       return sub_key;
   }

   public static void morph_cube (int counter, String k) {
       int shift;
       int ke;
       ArrayList<ArrayList<Integer>> section_shift;
       int mod_value = counter % alphabet_size;
       for (int z = 0; z < state.size(); z++) {
          for (int i = 0; i < k.length(); i++) {
             for (int y = 0; y < state.get(z).size(); y++) {
		 Collections.swap(state.get(z).get(y), mod_value, (int)k.charAt(i));
                 ke = (int)k.charAt(i);
             }
	  }
       }
   }
   
   public static String encrypt(String data, String key) {
       this.gen_cube(size_factor, size_factor, alphabet_size);
       this.key_cube(key);
       int sub, sub_pos, shift;
       String sub_key, ctxt;
       sub_key = key;
       for (int ctr = 0; ctr < data.length(); ctr++) {
          sub = data.charAt(ctr);
	  for (int z = 0; z < state.size(); z++) {
             for (int y = 0; y < state.get(z).size(); y++) {
	        sub_pos = sub;
		sub = state.get(z).get(y).get(sub_pos);
		shift = state.get(z).get(y).get(sub_pos);
		state.get(z).get(y).remove(shift);
		state.get(z).get(y).add(shift);
	     }
	  }
	  sub_key = key_scheduler(sub_key);
	  morph_cube(ctr, sub_key);
	  ctxt += (char) sub;
       }
       return ctxt;
    }
}
