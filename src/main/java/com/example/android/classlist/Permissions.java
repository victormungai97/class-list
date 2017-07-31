package com.example.android.classlist;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.provider.Settings;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AlertDialog;

/**
 * Created by User on 4/12/2017.
 * Class that checks for the app's permissions
 */

public class Permissions {

    // codes for various requests
    private static final int REQUEST_PHONE_STATE = 0;
    private static final int REQUEST_PHOTO = 1;
    private static final int REQUEST_LOCATION = 123;

    private static final String allow_message = "ALLOW";
    private static final String deny_message = "DENY";

    private Context mContext;

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

    /**
     * Method to redirect user to opening GPS from settings
     * @param context Current context of the app
     */
    void showSettingsAlert(Context context) {
        // create dialog
        mContext = context;
        AlertDialog.Builder alertDialog = new AlertDialog.Builder(mContext);

        // title of dialog
        alertDialog.setTitle("Missing GPS");
        // description of dialog
        alertDialog.setMessage("This app needs access to GPS");

        // if user clicks allow
        alertDialog.setPositiveButton(allow_message, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
                // Redirect to settings
                Intent intent = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
                mContext.startActivity(intent);
            }
        });

        // if user clicks deny
        alertDialog.setNegativeButton(deny_message, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
                // close dialog
                dialog.cancel();
            }
        });

        alertDialog.show();
    }
}
