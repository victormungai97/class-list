package com.example.android.classlist;

import android.content.Context;
import android.location.Location;
import android.os.Build;
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

    private String mast;

    private double mLatitude;
    private double mLongitude;
    private double mAltitude;
    private ArrayList<Double> locate = new ArrayList<>();

    public double getLatitude() {
        return mLatitude;
    }

    public void setLatitude(double latitude) {
        mLatitude = latitude;
    }

    public double getLongitude() {
        return mLongitude;
    }

    public void setLongitude(double longitude) {
        mLongitude = longitude;
    }

    public double getAltitude() {
        return mAltitude;
    }

    public void setAltitude(double altitude) {
        mAltitude = altitude;
    }

    LocatingClass(Context context, GoogleApiClient googleApiClient) {
        this.mContext = context;
        this.mClient = googleApiClient;
        //locationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        //turnGPSOn();
    }

    /**
     * Method builds location request to get a location fix
     */
    ArrayList<Double> findLocation(){
        //turnGPSOn();
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
                            LocatingClass.this.setLatitude(latitude);
                            LocatingClass.this.setLongitude(longitude);
                            LocatingClass.this.setAltitude(altitude);
                        }
                    });
        } catch (SecurityException ex){
            Log.e(TAG,"Error connecting to location.\n"+ex.getMessage());
        }

        return locate;
    }

    /**
     * Method to return details of the phone
     * @return String containing phone manufacturer, model and IMEI
     */
    String getPhone(){
        // used to get IMEI
        TelephonyManager telephonyManager = (TelephonyManager) mContext
                .getSystemService(Context.TELEPHONY_SERVICE);
        return Build.MANUFACTURER + " " + Build.MODEL + " " + Build.PRODUCT  + " "
                + telephonyManager.getDeviceId();
    }

    String getTime(){
        DateFormat df = DateFormat.getDateTimeInstance();
        Calendar calendar = Calendar.getInstance();
        return df.format(calendar.getTime());
    }

    /**
     * Checks whether mobile network is connected
     * @param context Context of app
     * @return status of connection
     */
    private static boolean isConnectedMobile(Context context) {
//        return ((TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE))
//                .getNetworkType() != TelephonyManager.NETWORK_TYPE_UNKNOWN;
        return true;
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
                primaryCellInfo.put("CID", ((GsmCellLocation) cellLocation).getCid() % 0xffff);
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
                assert cellInfos != null;
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
            assert cellInfos != null;
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
