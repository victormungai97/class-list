package com.example.android.classlist;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Point;

public class PictureUtilities {
    /*
    * Scales image file, calculates rate of scaling down to given area and then rereads the
    * file to create a scaled-down Bitmap object
     */
    public static Bitmap getScaledBitmap(String path, int destWidth, int destHeight){
        // Read in dimensions of the image on the disk
        BitmapFactory.Options options = new BitmapFactory.Options();

        float srcWidth = options.outWidth;
        float srcHeight = options.outHeight;

        // Figure out how much to scale down by
        int inSampleSize = 1; // determines how big each pixel in final image should be
        if (srcWidth > destWidth || srcHeight > destHeight){
            if(srcWidth > srcHeight){
                inSampleSize = Math.round(srcHeight / destHeight);
            } else {
                inSampleSize = Math.round(srcWidth / destWidth);
            }
        }

        options = new BitmapFactory.Options();
        options.inSampleSize = inSampleSize;

        // Read in and create final bitmap
        return BitmapFactory.decodeFile(path,options);
    }

    /*
    * Determines how big the ImageView is by getting a conservative estimate
     */
    public static Bitmap getScaledBitmap(String path, Activity activity){
        Point size = new Point();
        activity.getWindowManager().getDefaultDisplay().getSize(size);

        return getScaledBitmap(path, size.x, size.y);
    }

}
