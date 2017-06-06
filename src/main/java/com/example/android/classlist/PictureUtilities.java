package com.example.android.classlist;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Point;
import android.graphics.drawable.BitmapDrawable;
import android.media.FaceDetector;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.content.FileProvider;
import android.util.Log;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

class PictureUtilities {

    private static final int REQUEST_PHOTO = 1;
    private static String mCurrentPhotoPath;

    /*
    * Scales image file, calculates rate of scaling down to given area and then rereads the
    * file to create a scaled-down Bitmap object
     */
    private static Bitmap getScaledBitmap(String path, int destWidth, int destHeight){
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
    static Bitmap getScaledBitmap(String path, Activity activity){
        Point size = new Point();
        activity.getWindowManager().getDefaultDisplay().getSize(size);

        return getScaledBitmap(path, size.x, size.y);
    }


    /**
     * Method invokes intent to take picture
     */
    static Uri takePicture(Activity activity, String TAG){

        Uri imageForUpload = null;
        Context context = activity.getApplicationContext();

        // call phone's camera
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        // resolveActivity returns first activity component that can handle intent, preventing crash
        if (intent.resolveActivity(activity.getPackageManager()) != null){
            // Create file where image should go
            File photoFile;

            try{
                photoFile = getPhotoFile(context, TAG);
            } catch (Exception ex){
                Log.e("Image error","Error saving image");
                return null;
            }

            // continue only if File was successfully created
            if (photoFile != null) {
                Uri photoURI = FileProvider.getUriForFile(context,"com.example.android.fileprovider",
                        photoFile);
                intent.putExtra(MediaStore.EXTRA_OUTPUT,photoURI);
                imageForUpload = Uri.fromFile(photoFile);
                activity.startActivityForResult(intent, REQUEST_PHOTO);
                // photoFile.renameTo(new File(directory, getPhotoFilename()));
            }
        }

        return imageForUpload;
    }

    /**
     * Method makes file available for viewing from system's Media Provider
     */
    static void galleryAddPic(Activity activity) {
        Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
        File f = new File(mCurrentPhotoPath);
        Uri contentUri = Uri.fromFile(f);
        mediaScanIntent.setData(contentUri);
        activity.sendBroadcast(mediaScanIntent);
    }

    /**
     * Method returns the file containing the photo
     * @return photo file
     */
    private static File getPhotoFile(Context context, String TAG) {
        File externalFilesDir;
        externalFilesDir = context.getExternalFilesDir(Environment.DIRECTORY_PICTURES);

        // Save a file: path for use with ACTION_VIEW intents
        try {
            assert externalFilesDir != null;
            mCurrentPhotoPath = externalFilesDir.getAbsolutePath();
        } catch (NullPointerException ex){
            Log.e(TAG, ex.getMessage());
        }

        return new File(externalFilesDir, getPhotoFilename());
    }

    /**
     * Method return file name using the time that it was taken
     */
    private static String getPhotoFilename() {
        // get current time and set as file name
        DateFormat df = new SimpleDateFormat("ddMMyyyy_hhmmssSSS", Locale.ROOT);
        Calendar calendar = Calendar.getInstance();
        String time = df.format(calendar.getTime());
        return "IMG_" + time + ".jpg";
    }

    /**
     * Method to recognize and set faces after picture is taken
     * @param imageForUpload Uri of picture taken
     * @param imageView view to set picture to
     * @param activity activity of context
     * @return photo taken
     */
    static Bitmap recogniseFace(Uri imageForUpload, ImageView imageView, Activity activity){
        Bitmap photo;
        Context context = activity.getApplicationContext();

        activity.getContentResolver().notifyChange(imageForUpload,null);
        photo = getScaledBitmap(imageForUpload.getPath(),activity);

        if (photo != null) {
            // detect only one face to set to image view
            FaceDetector faceDet = new FaceDetector(photo.getWidth(), photo.getHeight(), 2);
            int faces = faceDet.findFaces(photo.copy(Bitmap.Config.RGB_565, false), new FaceDetector.Face[2]);
            if (faces == 0) {
                Toast.makeText(context, "No face Detected.", Toast.LENGTH_SHORT).show();
                imageView.setImageResource(android.R.drawable.ic_menu_camera);
                photo = null;
            } else if (faces > 1) {
                Toast.makeText(context, "Detected more than one face.", Toast.LENGTH_SHORT).show();
                imageView.setImageResource(android.R.drawable.ic_menu_camera);
                photo = null;
            }
            BitmapDrawable ob = new BitmapDrawable(activity.getResources(),photo);
            imageView.setImageDrawable(ob);
            // updateSubmitButtonState();
        } else {
            imageView.setImageResource(android.R.drawable.ic_menu_camera);
            Toast.makeText(context,"Error1 while capturing image",Toast.LENGTH_SHORT).show();
        }

        return photo;
    }
}
