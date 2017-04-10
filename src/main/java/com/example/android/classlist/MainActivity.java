package com.example.android.classlist;

import android.Manifest;
import android.app.Activity;
import android.app.Dialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.FaceDetector;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GooglePlayServicesUtil;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationServices;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.text.DateFormat;
import java.util.Calendar;


public class MainActivity extends AppCompatActivity {

    private ImageView mImageView;
    private String mCurrentPhotoPath;
    private Uri imageForUpload;
    private Button mButton;

    LocatingClass mLocatingClass; // instance of locating class
    GoogleApiClient mClient;

    private static final int REQUEST_ERROR = 0;
    private static final int REQUEST_PHOTO = 1;
    private static final int REQUEST_LOCATION = 123;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        /*
        This is called before initializing the camera because the camera needs permissions(the cause of the crash)
        */
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP ) {
            checkPermission();
        }

        mImageView = (ImageView) findViewById(R.id.image_view);
        mButton = (Button) findViewById(R.id.submit_btn);

        mImageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                takePicture();
                galleryAddPic();
            }
        });

        // client is instance of GoogleApiClient class and enables use of Play Services
        mClient = new GoogleApiClient.Builder(this)
                // add specific Play API to use ie Location API
                .addApi(LocationServices.API)
                // pass connection state information
                .addConnectionCallbacks(new GoogleApiClient.ConnectionCallbacks() {
                    @Override
                    public void onConnected(Bundle bundle) {
                        /*Toast.makeText(MainActivity.this,"Connected",Toast.LENGTH_SHORT)
                                .show();*/
                    }

                    @Override
                    public void onConnectionSuspended(int i) {
                        Toast.makeText(MainActivity.this,"Suspended",Toast.LENGTH_SHORT)
                                .show();
                    }
                })
                .build();

        mLocatingClass = new LocatingClass(getApplicationContext(),mClient);

        mButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                mLocatingClass.findLocation();
            }
        });

        //setPic();
    }

    @Override
    protected void onStart() {
        super.onStart();
        mClient.connect();
    }

    @Override
    protected void onStop() {
        super.onStop();
        mClient.disconnect();
    }

    /**
     * Method invokes intent to take picture
     */
    private void takePicture(){
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        // resolveActivity returns first activity component that can handle intent, preventing crash
        if (intent.resolveActivity(getPackageManager()) != null){
            // Create file where image should go
            File photoFile;

            try{
                photoFile = getPhotoFile();
            } catch (Exception ex){
                Log.e("Image error","Error saving image");
                return;
            }

            // continue only if File was successfully created
            if (photoFile != null) {
                Uri photoURI = FileProvider.getUriForFile(this,"com.example.android.fileprovider",
                        photoFile);
                intent.putExtra(MediaStore.EXTRA_OUTPUT,photoURI);
                imageForUpload = Uri.fromFile(photoFile);
                startActivityForResult(intent, REQUEST_PHOTO);
            }
        }
    }

    /**
     * Check on permission and redirect user to accept them
     */
    private void checkPermission(){
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED){
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CAMERA},REQUEST_PHOTO);
        }

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this,Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED
                ){
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},
                    REQUEST_LOCATION);

        }


    }

    /**
     * Method retrieves image sent by return intent as small Bitmap in extras with data as key
     * and displays to ImageView
     * @param requestCode request that was received from take picture
     * @param resultCode result of operation
     * @param data return intent
     */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        try {
            if (requestCode == REQUEST_PHOTO && resultCode == Activity.RESULT_OK) {
                if (imageForUpload != null) {
                    Uri selectedImage = imageForUpload;
                    getContentResolver().notifyChange(selectedImage,null);
                    Bitmap bitmap = getBitmap(imageForUpload.getPath());

                    if (bitmap != null) {
                        FaceDetector faceDet = new FaceDetector(bitmap.getWidth(), bitmap.getHeight(), 2);
                        int faces = faceDet.findFaces(bitmap.copy(Bitmap.Config.RGB_565, false), new FaceDetector.Face[2]);
                        if (faces == 0) {
                            Toast.makeText(this, "No face Detected.", Toast.LENGTH_SHORT).show();
                            bitmap = null;
                        } else if (faces > 1) {
                            Toast.makeText(this, "Detected more than one face.", Toast.LENGTH_SHORT).show();
                            bitmap = null;
                        }
                        mImageView.setImageBitmap(bitmap);
                    } else {
                        Toast.makeText(this,"Error1 while capturing image",Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(this,"Error2 while capturing image",Toast.LENGTH_SHORT).show();
                }
            }
        } catch (Exception ex) {
            Log.e("BITMAP error",ex.getMessage());
        }
    }

    /**
     * Method returns the file containing the photo
     * @return photo file
     */
    public File getPhotoFile() {
        // create file that saves in default images directory
        File externalFilesDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);

        // Save a file: path for use with ACTION_VIEW intents
        mCurrentPhotoPath = externalFilesDir.getAbsolutePath();

        return new File(externalFilesDir, getPhotoFilename());
    }

    /**
     * Method return file name using the time that it was taken
     */
    public String getPhotoFilename() {
        // get current time and set as file name
        DateFormat df = DateFormat.getDateTimeInstance();
        Calendar calendar = Calendar.getInstance();
        String time = df.format(calendar.getTime());
        return "IMG_" + time + ".jpg";
    }

    /**
     * Method makes file available for viewing from system's Media Provider
     */
    private void galleryAddPic() {
        Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
        File f = new File(mCurrentPhotoPath);
        Uri contentUri = Uri.fromFile(f);
        mediaScanIntent.setData(contentUri);
        this.sendBroadcast(mediaScanIntent);
    }

    /**
     * Method that decodes a scaled image from full size image
     */
    private Bitmap getBitmap(String path) {
        Uri uri = Uri.fromFile(new File(path));
        InputStream inputStream;
        try {
            // set max size of image
            final int IMAGE_MAX_SIZE = 1200000; // 1.2 MP
            inputStream = getContentResolver().openInputStream(uri);

            // Decode image size
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inJustDecodeBounds = true;
            BitmapFactory.decodeStream(inputStream,null,options);
            inputStream.close();

            int scale = 1;
            while ((options.outWidth * options.outHeight) * (1 / Math.pow(scale, 2)) > IMAGE_MAX_SIZE){
                scale++;
            }
            String msg = "scale = " + scale + ", original width: " + options.outWidth + "," +
                    " original height: " + options.outHeight;
            Log.d("",msg);

            Bitmap bitmap;
            inputStream = getContentResolver().openInputStream(uri);
            if (scale > 1){
                scale --;
                // Scale to max possible inSampleSize that still yields an image larger than target
                options = new BitmapFactory.Options();
                options.inSampleSize = scale;
                bitmap = BitmapFactory.decodeStream(inputStream,null,options);

                // resize to desired dimensions
                int height = bitmap.getHeight();
                int width = bitmap.getWidth();

                double destHeight = Math.sqrt(IMAGE_MAX_SIZE/ ((double) width) / height);
                double destWidth = (destHeight / height) * width;
                Bitmap scaledBitmap = Bitmap.createScaledBitmap(bitmap, (int) destWidth, (int) destHeight, true);
                bitmap.recycle();
                bitmap = scaledBitmap;

                System.gc();
            } else {
                bitmap = BitmapFactory.decodeStream(inputStream);
            }

            inputStream.close();
            msg = "Bitmap size - width: " + bitmap.getWidth() + ", height: " + bitmap.getHeight();
            Log.d("",msg);
            return  bitmap;
        } catch (IOException err){
            Log.e("IO Error",err.getMessage());
            return null;
        } catch (Exception ex){
            Log.e("Exception",ex.getMessage());
            return null;
        }
    }
}
