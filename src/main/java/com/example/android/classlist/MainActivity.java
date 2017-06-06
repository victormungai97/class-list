package com.example.android.classlist;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.location.LocationManager;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.text.Editable;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;
import android.text.TextWatcher;

import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationServices;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.util.ArrayList;

import static com.example.android.classlist.PictureUtilities.galleryAddPic;
import static com.example.android.classlist.PictureUtilities.recogniseFace;
import static com.example.android.classlist.PictureUtilities.takePicture;
import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.processResults;

public class MainActivity extends AppCompatActivity {

    private ImageView mImageView;
    private Uri imageForUpload;
    private Button mButton;
    private EditText full_name;
    private EditText adm_num;
    private EditText mServerUrl;

    private LocationManager locationManager;

    boolean mIsConnected = false;
    String name;
    String reg_no;
    int status = 0;
    String message;

    LocatingClass mLocatingClass; // instance of locating class
    GoogleApiClient mClient; // Google Play Services instance
    Bitmap photo = null;
    MyTextWatcher urlTextWatcher;
    MyTextWatcher nameWatcher;
    MyTextWatcher regWatcher;
    String mast;
    File directory;
    Context mContext;

    private static final String TAG = "MainActivity";
    private static final int REQUEST_PHOTO = 1;
    private static final String URL_TO_SEND_DATA = "http://192.168.43.229:5000/fromapp/";
    private static final String EXTRA_USER_FULL_NAME = "com.example.android.classlist.full_name";
    private static final String EXTRA_USER_REG_NUM = "com.example.android.classlist.reg_num";
    private static final String EXTRA_USER_DIR = "com.example.android.classlist.directory";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        /*
        This is called before initializing the camera because the camera needs permissions(the cause of the crash)
        Also checks for other dangerous permissions like location and phone network
        */
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP ) {
            Permissions.checkPermission(MainActivity.this, MainActivity.this);
        }

        mImageView = (ImageView) findViewById(R.id.image_view);
        mButton = (Button) findViewById(R.id.submit_btn);
        full_name = (EditText) findViewById(R.id.full_name);
        adm_num = (EditText) findViewById(R.id.admission_num);
        mServerUrl = (EditText) findViewById(R.id.ur_name_main);
        mContext = MainActivity.this;
        locationManager = (LocationManager) mContext.getSystemService(Context.LOCATION_SERVICE);
        mIsConnected = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER);

        try {
            mast = LocatingClass.getCellInfo(this).get("name").toString();
        } catch (JSONException ex){
            Log.e(MainActivity.class.toString(), ex.getMessage());
        }

        // get passed extras
        name = getIntent().getStringExtra(EXTRA_USER_FULL_NAME);
        reg_no = getIntent().getStringExtra(EXTRA_USER_REG_NUM);
        directory = new File(getIntent().getStringExtra(EXTRA_USER_DIR));

        urlTextWatcher = new MyTextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {

            }

            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {

            }

            @Override
            public void afterTextChanged(Editable editable) {
                empty = editable.toString().length() == 0;
                updateSubmitButtonState();
            }
        };

                nameWatcher = new MyTextWatcher() {
                    @Override
                    public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {

                    }

                    @Override
                    public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {

                    }

                    @Override
                    public void afterTextChanged(Editable editable) {
                        empty = editable.toString().length() == 0;
                        updateSubmitButtonState();
                    }
                };

                regWatcher = new MyTextWatcher() {
                    @Override
                    public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {

                    }

                    @Override
                    public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {

                    }

                    @Override
                    public void afterTextChanged(Editable editable) {
                        empty = editable.toString().length() == 0;
                        updateSubmitButtonState();
                    }
                };

        mServerUrl.addTextChangedListener(urlTextWatcher);
        full_name.addTextChangedListener(nameWatcher);
        adm_num.addTextChangedListener(regWatcher);

        mServerUrl.setText(URL_TO_SEND_DATA);
        full_name.setText(name);
        adm_num.setText(reg_no);

        //prevent edition
        if (name != null){
            full_name.setEnabled(false);
        }

        if (reg_no != null){
            adm_num.setEnabled(false);
        }

        turnGPSOn();
        imageForUpload = takePicture(MainActivity.this, TAG);
        galleryAddPic(MainActivity.this);

        mImageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                imageForUpload = takePicture(MainActivity.this, TAG);
                galleryAddPic(MainActivity.this);
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
                if (!mIsConnected) {
                    turnGPSOn();
                } else {
                    try {
                        ArrayList<Double> location = mLocatingClass.findLocation();
                        Log.i(TAG, location.toString());
                        String phone = mLocatingClass.getPhone();
                        String time = mLocatingClass.getTime();
                        String latitude = String.valueOf(mLocatingClass.getLatitude());
                        String longitude = String.valueOf(mLocatingClass.getLongitude());
                        JSONObject jsonObject = (JSONObject) LocatingClass.getCellInfo(MainActivity.this).get("primary");
                        String lac = String.valueOf(jsonObject.getInt("LAC")), ci = String.valueOf(jsonObject.getInt("CID"));

                        //JSONObject param = new JSONObject();
                        String name = full_name.getText().toString();
                        String regno = adm_num.getText().toString();

                        //ByteArrayOutputStream bos = new ByteArrayOutputStream();
                        //photo.compress(Bitmap.CompressFormat.PNG, 0 /*ignored for PNG*/, bos);
                        ByteArrayOutputStream baos = new ByteArrayOutputStream();
                        photo.compress(Bitmap.CompressFormat.JPEG, 100, baos); //bm is the bitmap object
                        byte[] byteArrayImage = baos.toByteArray();
                        String image = Base64.encodeToString(byteArrayImage, Base64.DEFAULT);
                        String url = mServerUrl.getText().toString();

                        new HttpsRequest().execute(name, regno, time, image, latitude, longitude, lac, ci, url, phone);
                        if (status == 0) {
                            Toast.makeText(MainActivity.this, message, Toast.LENGTH_SHORT).show();
                        } else {
                            Toast.makeText(MainActivity.this, message, Toast.LENGTH_SHORT).show();
                        }
                    } catch (JSONException ex) {
                        Log.e(TAG, "Error reading cell info " + ex.getMessage());
                    }
                }
            }
        });

        //setPic();
    }

    @Override
    public void onSaveInstanceState(Bundle b) {
        b.putParcelable("image", photo);
        b.putString("url", mServerUrl.getText().toString());
        b.putString("name", full_name.getText().toString());
        b.putString("reg", adm_num.getText().toString());
    }

    @Override
    public void onRestoreInstanceState(Bundle b) {
        photo = b.getParcelable("image");
        mImageView.setImageBitmap(photo);
        mServerUrl.setText(b.getString("url"));
        full_name.setText(b.getString("name"));
        adm_num.setText(b.getString("reg"));
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
     * Method checks whether information has been entered before submission
     */
    public void updateSubmitButtonState() {
        if (photo != null && urlTextWatcher.nonEmpty() && nameWatcher.nonEmpty() && regWatcher.nonEmpty()) {
            mButton.setEnabled(true);
        } else {
            mButton.setEnabled(false);
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
                    photo = recogniseFace(imageForUpload, mImageView, MainActivity.this);
                    updateSubmitButtonState();
                } else {
                    Toast.makeText(this,"Error2 while capturing image",Toast.LENGTH_SHORT).show();
                }
            }
        } catch (Exception ex) {
            Log.e("BITMAP error",ex.getMessage());
        }
    }


    /**
     * Checks whether field is empty
     */
    abstract class MyTextWatcher implements TextWatcher {
        boolean empty = true;

        boolean nonEmpty() {
            return !empty;
        }
    }

    private class HttpsRequest extends AsyncTask<String, Void, Void>{

        ProgressDialog pDialog = new ProgressDialog(MainActivity.this);

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            pDialog.setMessage("Please wait");
            pDialog.setIndeterminate(true);
            pDialog.show();
        }

        @Override
        protected Void doInBackground(String... jsonObjects) {
            String name = jsonObjects[0];
            String reg_no = jsonObjects[1];
            String time = jsonObjects[2];
            String pic = jsonObjects[3];
            String latitude = jsonObjects[4];
            String longitude = jsonObjects[5];
            String lac = jsonObjects[6];
            String ci = jsonObjects[7];
            String url = jsonObjects[8];
            String phone = jsonObjects[9];

            Message msg = new Message(name, reg_no, time, pic, latitude, longitude, lac, ci, phone);
            String TAG = "SIGNING IN SUCCESS ", ERROR = "Signing in Error: ";
            JSONObject jsonObject;
            jsonObject = processResults(TAG, POST(url,msg), ERROR);
            try {
                status = jsonObject.getInt("STATUS");
                message = jsonObject.getString("MESSAGE");
            } catch (JSONException ex){
                Log.e("JSON error", "Error sending data "+ex.getMessage());
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void aVoid) {
            super.onPostExecute(aVoid);
            if (pDialog.isShowing()){
                pDialog.cancel();
            }
        }
    }

    /**
     * Method to called in RegisterActivity to create Intent containing extra info as needed.
     * Helps to hide MainActivity's needed extras
     * @param packageContext current context of application
     * @param full_name user's full name
     * @param reg_num user's registration number
     * @return intent to be created
     */
    public static Intent newIntent(Context packageContext, String full_name, String reg_num,
                                   String dir) {
        Intent i = new Intent(packageContext, MainActivity.class);
        i.putExtra(EXTRA_USER_FULL_NAME, full_name);
        i.putExtra(EXTRA_USER_REG_NUM, reg_num);
        i.putExtra(EXTRA_USER_DIR, dir);
        return i;
    }

    /**
     * Method to check whether GPS is on
     */
    private void turnGPSOn(){
        mIsConnected = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER);
        if (!mIsConnected){
            //Toast.makeText(mContext,"This app needs GPS. Please turn on",Toast.LENGTH_SHORT).show();
            new Permissions().showSettingsAlert(mContext);
        }
    }
}
