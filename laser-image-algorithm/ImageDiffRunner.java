import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

public class ImageDiffRunner
{
    public static void main(String[] args)
    {
        String dirPath = ".\\image",
                laserOnPath = dirPath + "\\on.bmp",
                laserOffPath = dirPath + "\\off.bmp",
                outputPath = dirPath + "\\out.bmp";
        
        ImageMagickDiff laserFinder = new ImageMagickDiff(laserOnPath, laserOffPath, outputPath);
		
        try {
			File outFile = new File(outputPath);
			if(outFile.exists()) outFile.delete();
			outFile.createNewFile();
		} catch(IOException e) {
			System.err.println(e.getMessage());
		}
        
        long timeStart = System.nanoTime();
        laserFinder.diff();
        long timeEnd = System.nanoTime();
        
        //ImageMagickDiff.display(outputPath);
        
        long millis = TimeUnit.NANOSECONDS.toMillis(timeEnd-timeStart);
        System.out.println("Process completed in " + millis + " milliseconds");
    }
}
