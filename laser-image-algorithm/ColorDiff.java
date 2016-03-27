import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

public class ColorDiff 
{
    public static void colorDiff(String pathLaserOn, String pathLaserOff, String pathOutput) 
    {
        BufferedImage imgLaserOn, imgLaserOff;
        //String pathLaserOn = "C:/Users/Evan/Documents/RobotX/laseron1.jpeg";
        //String pathLaserOff = "C:/Users/Evan/Documents/RobotX/laseroff1.jpeg";
        //String pathOutput = "C:/Users/Evan/Documents/RobotX/laserdiff1.jpeg";
        boolean debugOutput = false;
        
        // load images from files
        if(debugOutput) System.out.println("Loading images from files...");
        try {
            imgLaserOn = ImageIO.read(new File(pathLaserOn));
            imgLaserOff = ImageIO.read(new File(pathLaserOff));
        } catch (IOException e) {
            System.out.println("process failed");
            System.exit(1);
            imgLaserOn = null;
            imgLaserOff = null;
        }
        
        long timeStart = System.currentTimeMillis();
        
        // load rgb vectors from images
        // note: images must be the same resolution
        if(debugOutput) System.out.println("Loading RGB vectors from images...");
        int imgWidth = imgLaserOn.getWidth();
        int imgHeight = imgLaserOn.getHeight();
        int[] rgbLaserOn = new int[imgWidth * imgHeight];
        int[] rgbLaserOff = new int[imgWidth * imgHeight];
        imgLaserOn.getRGB(0, 0, imgWidth, imgHeight, rgbLaserOn, 0, imgWidth);
        imgLaserOff.getRGB(0, 0, imgWidth, imgHeight, rgbLaserOff, 0, imgWidth);
        
        // use laser off image to mask laser on image
        if(debugOutput) System.out.println("Subtracting image values...");
        int[] rgbDiff = new int[rgbLaserOn.length];
        //System.out.println("rgbDiff is size " + rgbDiff.length);
        for(int i = 0; i < rgbDiff.length; i++) {
            Color con = new Color( rgbLaserOn[i] ); //opaque color of pixel
            Color coff = new Color( rgbLaserOff[i] );
            Color colorDiff = new Color ( 
                    diffNonNegative(con.getRed(), coff.getRed()), 
                    diffNonNegative(con.getGreen(), coff.getGreen()), 
                    diffNonNegative(con.getBlue(), coff.getBlue())   );
            rgbDiff[i] = colorDiff.getRGB();
            //if(debugOutput && i%100000==0) System.out.println("Pixel " + i + " is " + rgbDiff[i]);
        }
        
        // load rgb vals into an new image
        if(debugOutput) System.out.println("Loading RGB diff into new image...");
        BufferedImage imgDiff = new BufferedImage(imgWidth, imgHeight, BufferedImage.TYPE_INT_RGB);
        imgDiff.setRGB(0, 0, imgWidth, imgHeight, rgbDiff, 0, imgWidth);
        
        long timeEnd = System.currentTimeMillis();
        
        try {
            //FileOutputStream fis = new FileOutputStream(new File(pathOutput));
            File outputFile = new File(pathOutput);
            outputFile.createNewFile();
            ImageIO.write(imgDiff, "jpeg", outputFile);
        } catch(Exception e) {
            System.out.println("process failed");
            System.exit(1);
        }
        
        System.out.println("Done: " + (timeEnd-timeStart) + " milliseconds");
        
    }
    
    static int diffNonNegative(int n1, int n2) {
        return Math.max( n1-n2 , 0 );
    }
}
