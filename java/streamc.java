import java.net.*;
import java.io.*;
import java.util.*;

public class streamc {
   public static void main(String[] args) {
      String serverName = "thrash.hacked.jp";
      int port = 31234;
      try {
         Socket client = new Socket(serverName, port);
         //System.out.println("Just connected to " + client.getRemoteSocketAddress());
         //InputStream in = client.getInputStream();
	 //DataOutputStream out = new DataOutputStream(client.getOutputStream());
	 InputStreamReader isr = new InputStreamReader(client.getInputStream());
	 BufferedReader in = new BufferedReader(isr);
	 PrintWriter out = new PrintWriter(client.getOutputStream(), true);
	 int l_prompt;
	 for (int x = 0; x < 7; x++) {
		l_prompt = in.read();
	 	System.out.print((char)l_prompt);
	 }
	 Scanner scanner = new Scanner(System.in);
	 String login = scanner.nextLine();
	 out.println(login);
	 
	 int p_prompt;
	 for (int x = 0; x < 10; x++) {
		p_prompt = in.read();
	 	System.out.print((char)p_prompt);
	 }
	 String passwd = scanner.nextLine();
	 out.println(passwd);
	 String smsg;
	 while (true) {
		while ((smsg = in.readLine()) != null) {
			//System.out.print((char)smsg);
			System.out.println(smsg);
			if (in.ready() == false) {
				break;
			}
		}
		smsg = in.readLine();
		System.out.print(smsg);
	 	String msg = scanner.nextLine();
	 	out.println(msg);
		if (msg == "exit") {
			break;
		}
		
	}
         
        client.close();
      }catch(IOException e) {
         e.printStackTrace();
      }
   }
}
