package com.example.android.classlist;

import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.location.Location;
import android.location.LocationManager;
import android.provider.Settings;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.widget.Toast;

import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;

import java.text.DateFormat;
import java.util.Calendar;

/**
 * Created by Victor Mungai on 4/8/2017.
 */

class LocatingClass {

    private final Context mContext;
    private final GoogleApiClient mClient;
    private static final String TAG = "LocationActivity";
    private static final String allow_message = "ALLOW";
    private static final String deny_message = "DENY";

    LocationManager locationManager;
    boolean isConnected = false;

    LocatingClass(Context context, GoogleApiClient googleApiClient) {
        this.mContext = context;
        this.mClient = googleApiClient;
        locationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        turnGPSOn();
    }

    void turnGPSOn(){
        isConnected = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER);
        if (!isConnected){
            Toast.makeText(mContext,"This app needs GPS. Please turn on",Toast.LENGTH_SHORT).show();
            //showSettingsAlert();
        }
    }

    /**
     * Method builds location request to get a location fix
     */
    void findLocation(){
        turnGPSOn();
        LocationRequest locationRequest = LocationRequest.create();
        // set priority between battery life and accuracy
        locationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
        // set how many times location should be updated
        locationRequest.setNumUpdates(1);
        // set how frequently location should be updated
        locationRequest.setInterval(0);
        // send off request and listen for locations that come back

        try {
            LocationServices.FusedLocationApi
                    .requestLocationUpdates(mClient, locationRequest, new LocationListener() {
                        @Override
                        public void onLocationChanged(Location location) {
                            Log.i(TAG, "Got a fix: " + location);
                            double latitude = location.getLatitude();
                            double longitude = location.getLongitude();
                            String message = "Latitude: " + Double.toString(latitude)
                                    + "\nLongitude: " + Double.toString(longitude)
                                    + "\nTime: " + getTime();
                            Toast.makeText(mContext, message, Toast.LENGTH_SHORT).show();
                        }
                    });
        } catch (SecurityException ex){
            Log.e(TAG,"Error connecting to location.\n"+ex.getMessage());
        }
    }

    private String getTime(){
        DateFormat df = DateFormat.getDateInstance();
        Calendar calendar = Calendar.getInstance();
        return df.format(calendar.getTime());
    }

    public void showSettingsAlert() {
        // create dialog
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
