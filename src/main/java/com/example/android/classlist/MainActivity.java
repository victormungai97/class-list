package com.example.android.classlist;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.drawable.BitmapDrawable;
import android.media.FaceDetector;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.content.FileProvider;
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
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Calendar;

import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.processResults;

public class MainActivity extends AppCompatActivity {

    private ImageView mImageView;
    private String mCurrentPhotoPath;
    private Uri imageForUpload;
    private Button mButton;
    private EditText full_name;
    private EditText adm_num;
    private EditText mServerUrl;
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

    private static final String TAG = "MainActivity";
    private static final int REQUEST_PHOTO = 1;
    private static final String URL_TO_SEND_DATA = "http://192.168.43.229:5000/fromapp/";
    private static final String EXTRA_USER_FULL_NAME = "com.example.android.classlist.full_name";
    private static final String EXTRA_USER_REG_NUM = "com.example.android.classlist.reg_num";

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
        try {
            mast = LocatingClass.getCellInfo(this).get("name").toString();
        } catch (JSONException ex){
            Log.e(MainActivity.class.toString(), ex.getMessage());
        }

        // get passed extras
        name = getIntent().getStringExtra(EXTRA_USER_FULL_NAME);
        reg_no = getIntent().getStringExtra(EXTRA_USER_REG_NUM);

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
                try {
//                    mLocatingClass.findLocation();
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
                    if (status == 0){
                        Toast.makeText(MainActivity.this,message,Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(MainActivity.this,message,Toast.LENGTH_SHORT).show();
                    }
                } catch (JSONException ex){
                    Log.e(TAG, "Error reading cell info "+ex.getMessage());
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
     * Method invokes intent to take picture
     */
    private void takePicture(){

        // call phone's camera
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
                    photo = PictureUtilities.getScaledBitmap(imageForUpload.getPath(),MainActivity.this);

                    if (photo != null) {
                        FaceDetector faceDet = new FaceDetector(photo.getWidth(), photo.getHeight(), 2);
                        int faces = faceDet.findFaces(photo.copy(Bitmap.Config.RGB_565, false), new FaceDetector.Face[2]);
                        if (faces == 0) {
                            Toast.makeText(this, "No face Detected.", Toast.LENGTH_SHORT).show();
                            mImageView.setImageResource(android.R.drawable.ic_menu_camera);
                            photo = null;
                        } else if (faces > 1) {
                            Toast.makeText(this, "Detected more than one face.", Toast.LENGTH_SHORT).show();
                            mImageView.setImageResource(android.R.drawable.ic_menu_camera);
                            photo = null;
                        }
                        BitmapDrawable ob = new BitmapDrawable(getResources(),photo);
                        mImageView.setImageDrawable(ob);
                        updateSubmitButtonState();
                    } else {
                        mImageView.setImageResource(android.R.drawable.ic_menu_camera);
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
    public static Intent newIntent(Context packageContext, String full_name, String reg_num) {
        Intent i = new Intent(packageContext, MainActivity.class);
        i.putExtra(EXTRA_USER_FULL_NAME, full_name);
        i.putExtra(EXTRA_USER_REG_NUM, reg_num);
        return i;
    }
}
