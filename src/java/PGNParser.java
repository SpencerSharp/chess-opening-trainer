import java.io.File;

public class PGNParser {

    public static void main(String[] args) {

        BufferedReader in = new BufferedReader(new FileReader("foo.in"));

        boolean isGame = true;
        boolean inBrackets = false;
        boolean lookingForWhiteMove = false;
        boolean lookingForBlackMove = false;
        boolean lookingForDot = true;

        String dense = "";

        for(int i = 0; i < 20; i++) {
            String line = in.readLine();
            String move = "";

            if (line.equals("\n")) {
                if (isGame) {
                    isGame = false;
                    char c = in.read();

                    int mv = 0;

                    while (cnt < 15) {
                        c = in.read();
                        if (inBrackets) {
                            if (c == '}') {
                                inBrackets = false;
                            }
                        } else if (c == '{') {
                            inBrackets = true;
                        } else if (lookingForDot) {
                            if (c == '.') {
                                mv++;
                                lookingForDot = false;
                                lookingForWhiteMove = true;
                            }
                        } else if (c == ' ') {
                            dense += move + "|";
                            if (lookingForWhiteMove) {
                                lookingForWhiteMove = false;
                                lookingForBlackMove = true;
                            } else if (lookingForBlackMove) {
                                lookingForBlackMove = false;
                                lookingForDot = true;
                            }
                        } else if (lookingForWhiteMove) {
                            move += c;
                        } else if (lookingForBlackMove) {
                            move += c;
                        }
                    }

                    dense += "\n";

                    in.readLine();
                } else {
                    isGame = true;
                }
            }
        }

        System.out.println(dense);
    }

    public char[] compressFEN(String fen) {

    }
}