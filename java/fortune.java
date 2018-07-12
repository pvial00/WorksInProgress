import java.net.*;
import java.io.*;
import java.util.*;

public class fortune {
   public static void main(String[] args) {
      String serverName = "thrash.hacked.jp";
      int port = 34568;
   try {
         Socket client = new Socket(serverName, port);
         InputStream in = client.getInputStream();
	 DataOutputStream out = new DataOutputStream(client.getOutputStream());
	 int fortune;
	 while ((fortune = in.read()) !=-1) {
	 	System.out.print((char)fortune);
       	 }
        //client.close();
      }catch(IOException e) {
         e.printStackTrace();
      }
   }
}
