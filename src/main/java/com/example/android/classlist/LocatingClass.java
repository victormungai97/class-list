package com.example.android.classlist;

import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.location.Location;
import android.location.LocationManager;
import android.os.Build;
import android.provider.Settings;
import android.support.v7.app.AlertDialog;
import android.telephony.CellIdentityCdma;
import android.telephony.CellIdentityGsm;
import android.telephony.CellIdentityLte;
import android.telephony.CellIdentityWcdma;
import android.telephony.CellInfo;
import android.telephony.CellInfoCdma;
import android.telephony.CellInfoGsm;
import android.telephony.CellInfoLte;
import android.telephony.CellInfoWcdma;
import android.telephony.CellLocation;
import android.telephony.TelephonyManager;
import android.telephony.cdma.CdmaCellLocation;
import android.telephony.gsm.GsmCellLocation;
import android.util.Log;
import android.widget.Toast;

import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

/***
 * Created by Victor Mungai on 4/8/2017.
 */

class LocatingClass {

    private final Context mContext;
    private final GoogleApiClient mClient;
    private static final String TAG = "LocationActivity";
    private static final String allow_message = "ALLOW";
    private static final String deny_message = "DENY";

    private String mast;
    private LocationManager locationManager;
    private boolean isConnected = false;

    LocatingClass(Context context, GoogleApiClient googleApiClient) {
        this.mContext = context;
        this.mClient = googleApiClient;
        locationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        turnGPSOn();
    }

    private void turnGPSOn(){
        isConnected = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER);
        if (!isConnected){
            Toast.makeText(mContext,"This app needs GPS. Please turn on",Toast.LENGTH_SHORT).show();
            //showSettingsAlert();
        }
    }

    /**
     * Method builds location request to get a location fix
     */
    ArrayList<Double> findLocation(){
        final ArrayList<Double> locate = new ArrayList<>();
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
                            double altitude = location.getAltitude();
                            try {
                                mast = getCellInfo(mContext).get("name").toString();
                            } catch (JSONException ex){
                                Log.e(TAG, "Error connecting to network");
                            }
                            String phone = getPhone();
                            String message = "Latitude: " + Double.toString(latitude)
                                    + "\nLongitude: " + Double.toString(longitude)
                                    + "\nAltitude: " + Double.toString(altitude)
                                    + "\nTime: " + getTime()
                                    + "\nPhone: " + phone
                                    + "\nMast: " + mast;
                            Toast.makeText(mContext, message, Toast.LENGTH_SHORT).show();
                            locate.add(latitude);
                            locate.add(longitude);
                            locate.add(altitude);
                        }
                    });
        } catch (SecurityException ex){
            Log.e(TAG,"Error connecting to location.\n"+ex.getMessage());
        }

        return locate;
    }

    String getPhone(){
        return Build.MANUFACTURER + " " + Build.MODEL + " " + Build.PRODUCT;
    }

    String getTime(){
        DateFormat df = DateFormat.getDateTimeInstance();
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

    /**
     * Checks whether mobile network is connected
     * @param context Context of app
     * @return status of connection
     */
    private static boolean isConnectedMobile(Context context) {
        return ((TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE))
                .getNetworkType() != TelephonyManager.NETWORK_TYPE_UNKNOWN;
    }

    /**
     * Method to get connection information of mobile network
     * @param context Context of app
     * @return JSONObject of network
     */
    static JSONObject getCellInfo(Context context) {
        JSONObject cellList = new JSONObject();
        if (!isConnectedMobile(context))
            return cellList;

        TelephonyManager tel = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
        JSONObject primaryCellInfo = new JSONObject();
        JSONArray secondaryCellInfos = new JSONArray();
        CellLocation cellLocation = tel.getCellLocation();
        List<CellInfo> cellInfos = null;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
            cellInfos = tel.getAllCellInfo();
        }

        // Getting primary info
        if (cellLocation instanceof GsmCellLocation) {
            try {
                primaryCellInfo.put("type", tel.getNetworkType());
                primaryCellInfo.put("Operator", tel.getNetworkOperator());
                primaryCellInfo.put("LAC", ((GsmCellLocation) cellLocation).getLac());
                primaryCellInfo.put("CID", ((GsmCellLocation) cellLocation).getCid() % 0x10000);
            } catch (Exception e) {
                Log.e("Network error", e.getMessage());
            }
        } else if (cellLocation instanceof CdmaCellLocation) {
            try {
                primaryCellInfo.put("type", tel.getNetworkType());
                primaryCellInfo.put("Operator", tel.getNetworkOperator());
                primaryCellInfo.put("NID", ((CdmaCellLocation) cellLocation).getNetworkId());
                primaryCellInfo.put("BID", ((CdmaCellLocation) cellLocation).getBaseStationId() % 0x10000);
            } catch (Exception e) {
                Log.e("Network error", e.getMessage());
            }
        } else if (cellLocation == null) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
                for (CellInfo cellInfo : cellInfos) {
                    if (cellInfo instanceof CellInfoLte) {
                        CellIdentityLte lte = ((CellInfoLte) cellInfo).getCellIdentity();
                        try {
                            primaryCellInfo.put("type", tel.getNetworkType());
                            primaryCellInfo.put("Operator", tel.getNetworkOperator());
                            primaryCellInfo.put("TAC", lte.getTac());
                            primaryCellInfo.put("GIC", lte.getCi());
                        } catch (Exception e) {
                            Log.e("Network error", e.getMessage());
                        }
                    }
                }
            }
        }

        // Getting secondary info
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
            for (CellInfo cellInfo : cellInfos) {
                JSONObject secondaryCellInfo = new JSONObject();
                if (cellInfo instanceof CellInfoLte) {
                    CellIdentityLte lte = ((CellInfoLte) cellInfo).getCellIdentity();
                    try {
                        secondaryCellInfo.put("TAC", lte.getTac());
                        secondaryCellInfo.put("GIC", lte.getCi() % 0x10000);
                    } catch (Exception e) {
                        Log.e("Network error", e.getMessage());
                    }
                } else if (cellInfo instanceof CellInfoCdma) {
                    CellIdentityCdma cdma = ((CellInfoCdma) cellInfo).getCellIdentity();
                    try {
                        secondaryCellInfo.put("NID", cdma.getNetworkId());
                        secondaryCellInfo.put("BID", cdma.getBasestationId() % 0x10000);
                    } catch (Exception e) {
                        Log.e("Network error", e.getMessage());
                    }
                } else if (cellInfo instanceof CellInfoGsm) {
                    CellIdentityGsm gsm = ((CellInfoGsm) cellInfo).getCellIdentity();
                    try {
                        secondaryCellInfo.put("LAC", gsm.getLac());
                        secondaryCellInfo.put("CID", gsm.getCid() % 0x10000);
                    } catch (Exception e) {
                        Log.e("Network error", e.getMessage());
                    }
                }

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR2 && cellInfo instanceof CellInfoWcdma) {
                    CellIdentityWcdma wcdma = ((CellInfoWcdma) cellInfo).getCellIdentity();
                    try {
                        secondaryCellInfo.put("LAC", wcdma.getLac());
                        secondaryCellInfo.put("CID", wcdma.getCid() % 0x10000);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
                secondaryCellInfos.put(secondaryCellInfo);
            }
        }

        try {
            cellList.put("primary", primaryCellInfo);
            cellList.put("secondary", secondaryCellInfos);
        } catch (Exception e) {
            e.printStackTrace();
        }

        return cellList;
    }
}
