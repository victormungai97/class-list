package com.example.android.classlist;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;

/**
 * Created by User on 4/12/2017.
 */

public class Permissions {

    // codes for various requests
    private static final int REQUEST_PHONE_STATE = 0;
    private static final int REQUEST_PHOTO = 1;
    private static final int REQUEST_LOCATION = 123;

    /**
     * Check on permissions and redirect user to accept them
     */
    public static void checkPermission(Context context, Activity activity){
        // permission for camera
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED){
            ActivityCompat.requestPermissions(activity, new String[]{Manifest.permission.CAMERA},REQUEST_PHOTO);
        }

        // permission for location/GPS
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(context,Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED
                ){
            ActivityCompat.requestPermissions(activity,
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},
                    REQUEST_LOCATION);
        }

        // permission for network
        if (ContextCompat.checkSelfPermission(context,Manifest.permission.READ_PHONE_STATE) != PackageManager.PERMISSION_GRANTED){
            ActivityCompat.requestPermissions(activity, new String[]{Manifest.permission.READ_PHONE_STATE}, REQUEST_PHONE_STATE);
        }

    }
}
