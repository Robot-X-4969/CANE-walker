import java.io.IOException;

public class ImageMagickDiff 
{
    private final static String[] staticArgs = {
        "cmd /c composite ",
        " -compose difference - | convert - -colorspace Gray -auto-level -black-threshold 90%% -white-threshold 90%% "
    };
    
    private String cmd;
    private Runtime rt;
    
    public ImageMagickDiff(String img1Path, String img2Path, String imgOutPath) {
        cmd = staticArgs[0] + img1Path + " " + img2Path + staticArgs[1] + imgOutPath;
        rt = Runtime.getRuntime();
    }
    
    public void diff() {
        try {
            Process p = rt.exec(cmd);
            p.waitFor();
        } catch(IOException | InterruptedException e) {
            System.err.println(e.getMessage());
        }
    }
    
    public static void display(String imgPath) {
        try {
            Runtime.getRuntime().exec("cmd /c imdisplay " + imgPath);
        } catch(IOException e) {
            System.err.println(e.getMessage());
        }
    }
    
}
