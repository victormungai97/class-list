package com.example.android.classlist;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
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

import com.android.internal.http.multipart.Part;
import com.android.internal.http.multipart.StringPart;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationServices;

import org.apache.http.HttpEntity;
import org.apache.http.HttpRequest;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.entity.mime.MultipartEntity;
import org.apache.http.entity.mime.content.ByteArrayBody;
import org.apache.http.entity.mime.content.StringBody;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.UnsupportedEncodingException;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Iterator;
import java.util.List;

import static com.example.android.classlist.R.id.ur_name;

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

    LocatingClass mLocatingClass; // instance of locating class
    GoogleApiClient mClient;
    Bitmap photo = null;
    MyTextWatcher urlTextWatcher;
    MyTextWatcher nameWatcher;
    MyTextWatcher regWatcher;
    String mast;
    String statusCode;

    private static final String TAG = "MainActivity";
    private static final int REQUEST_PHOTO = 1;
    private static final String URL_TO_SEND_DATA = "http://192.168.0.11:5000/enternew";
    private static final String EXTRA_USER_FIRST_NAME = "com.example.android.classlist.first_name";
    private static final String EXTRA_USER_LAST_NAME = "com.example.android.classlist.last_name";
    private static final String EXTRA_USER_REG_NUM = "com.example.android.classlist.reg_num";

    private static final String NAME = "name";
    private static final String REG_NO = "regno";
    private static final String PIC = "picture";
    private static final String TIME = "time";
    //private static final String GPS = "gps";
    private static final String LATITUDE = "latitude";
    private static final String LONGITUDE = "longitude";
    private static final String LAC = "lac";
    private static final String CI = "ci";

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
        mServerUrl = (EditText) findViewById(ur_name);
        try {
            mast = LocatingClass.getCellInfo(this).get("name").toString();
        } catch (JSONException ex){
            Log.e(MainActivity.class.toString(), ex.getMessage());
        }

        // get passed extras
        name = getIntent().getStringExtra(EXTRA_USER_FIRST_NAME) + " " +
                getIntent().getStringExtra(EXTRA_USER_LAST_NAME);
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
                if (editable.toString().length() == 0) {
                    empty = true;
                } else {
                    empty = false;
                }
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
                        if (editable.toString().length() == 0) {
                            empty = true;
                        } else {
                            empty = false;
                        }
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
                        if (editable.toString().length() == 0) {
                            empty = true;
                        } else {
                            empty = false;
                        }
                        updateSubmitButtonState();
                    }
                };

        mServerUrl.addTextChangedListener(urlTextWatcher);
        full_name.addTextChangedListener(nameWatcher);
        adm_num.addTextChangedListener(regWatcher);

        mServerUrl.setText(URL_TO_SEND_DATA);
        full_name.setText(name);
        adm_num.setText(reg_no);

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
                ArrayList<Double> location = mLocatingClass.findLocation();
                String phone = mLocatingClass.getPhone();
                String time = mLocatingClass.getTime();
                String latitude = "0";
                String longitude = "0";
                String lac = "0", ci = "0";

                //JSONObject param = new JSONObject();
                String name = full_name.getText().toString();
                String regno = adm_num.getText().toString();

                //ByteArrayOutputStream bos = new ByteArrayOutputStream();
                //photo.compress(Bitmap.CompressFormat.PNG, 0 /*ignored for PNG*/, bos);
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                photo.compress(Bitmap.CompressFormat.JPEG, 100, baos); //bm is the bitmap object
                byte[] byteArrayImage = baos.toByteArray();
                String image = Base64.encodeToString(byteArrayImage, Base64.DEFAULT);

                new HttpsRequest().execute(name, regno, time, image, latitude, longitude, lac, ci);
                //try {
                    //image.put(PIC, bos.toByteArray());
                    //param.put("name", full_name.getText().toString());
                    //param.put("regno", adm_num.getText().toString());
                    //param.put("time", timeIn);
                    /*param.put("latitude",location.get(0));
                    param.put("longitude", location.get(1));
                    param.put("altitude",location.get(2));
                    param.put("phone", phone);
                    param.put("mast", mast);*/
                    //new HttpRequest().execute(param,image);
                /*} catch (JSONException ex){
                    Log.e(MainActivity.class.toString(), ex.getMessage());
                }*/
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
     * Checks whether field is empty
     */
    public abstract class MyTextWatcher implements TextWatcher {
        boolean empty = true;

        public boolean nonEmpty() {
            return !empty;
        }
    }

    private class HttpsRequest extends AsyncTask<String, Void, Void>{

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

            // preparing post params using namevalue pair
            List<NameValuePair> params = new ArrayList<>();
            params.add(new BasicNameValuePair(NAME,name));
            params.add(new BasicNameValuePair(REG_NO,reg_no));
            params.add(new BasicNameValuePair(TIME, time));
            params.add(new BasicNameValuePair(PIC, pic));
            params.add(new BasicNameValuePair(LATITUDE, latitude));
            params.add(new BasicNameValuePair(LONGITUDE, longitude));
            params.add(new BasicNameValuePair(LAC, lac));
            params.add(new BasicNameValuePair(CI, ci));

            ServiceHandler serviceClient = new ServiceHandler();

            // create response
            String json = serviceClient.makeServiceCall(URL_TO_SEND_DATA,ServiceHandler.POST,params);

            Log.d("Create Request: ", "> " + json);
            if (json != null) {
                try {
                    // convert string to json object
                    Log.i(TAG, json);
                    JSONObject jsonObj = new JSONObject(json);
                    boolean error = jsonObj.getBoolean("error");
                    // checking for error node in json
                    if (!error) {
                        // new category created successfully
                        Log.e("ADDITION SUCCESS ",
                                "> " + jsonObj.getString("message"));
                    } else {
                        Log.e("Add Prediction Error: ",
                                "> " + jsonObj.getString("message"));
                    }

                } catch (JSONException e) {
                    e.printStackTrace();
                }

            } else {
                Log.e("JSON Data", "JSON data error!");
            }

            return null;
        }
    }

    /**
     * class to perform communication with server and sending of data
     * Params, the type of the parameters sent to the task upon execution.
     * Here, three string variables are sent to the background task, so type is String.
     * Progress, the type of the progress units published during the background computation.
     * We are not using any progress units here, so type is Void.
     * Result, the type of the result of the background computation.
     * As we are not using the result, the type is Void.

     */
    /*private class HttpRequest extends AsyncTask<JSONObject, Void, Void> {
        private ProgressDialog dialog = new ProgressDialog(MainActivity.this);
        long start;

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            dialog.setMessage("Please wait");
            dialog.show();
            start = System.currentTimeMillis();
        }

        @Override
        protected Void doInBackground(JSONObject... arg) {
            System.out.println("doInBackground");
            try {
                // Preparing multipart-form params
                Iterator<String> keys = arg[0].keys();
                List<Part> parts = new ArrayList<>();

                String boundary = "-------------" + System.currentTimeMillis();
                MultipartEntity partsBuilder = new MultipartEntity();
                while (keys.hasNext()) {
                    String name = keys.next();
                    StringPart stringPart = new StringPart(name, arg[0].getString(name));
                    parts.add(stringPart);
                    partsBuilder.addPart(name, new StringBody(arg[0].getString(name)));
                }

                // setting image value
                byte[] image = (byte[]) arg[1].get("image");
                System.out.println("size: " + image.length);
                partsBuilder.addPart("image", new ByteArrayBody(image, "image.png"));
                /*FilePart filePart = new FilePart("image", new ByteArrayPartSource("afile", image));
                parts.add(filePart);*/

                /*HttpEntity entity = partsBuilder;
                ServiceHandler serviceClient = new ServiceHandler();

                HttpResponse httpResponse = null;
                try {
                    String html = ServiceHandler.responseToString(httpResponse = serviceClient.makeMultiPartPost(URL_TO_SEND_DATA,
                            entity));
                    /* For debugging */
                    // System.out.println("html: " + html);
                /*} catch (IllegalArgumentException e) {

                }

                if (httpResponse != null)
                    statusCode = Integer.toString(httpResponse.getStatusLine().getStatusCode());
                else
                    statusCode = "Server Not Found!";

                Log.i("Status", statusCode);

                if (!statusCode.equals("") && !statusCode.matches("2\\d\\d"))
                    MainActivity.this.runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(MainActivity.this, "Status: " + statusCode, Toast.LENGTH_LONG).show();
                        }
                    });
                else
                    MainActivity.this.runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(MainActivity.this, "Okay", Toast.LENGTH_SHORT).show();
                        }
                    });
            } catch (JSONException | UnsupportedEncodingException e) {
                e.printStackTrace();
            }

            long timeCost = System.currentTimeMillis() - start;
            if (timeCost < 2000L) {
                try {
                    Thread.sleep(2000L - timeCost);
                } catch (InterruptedException e) {

                }
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            super.onPostExecute(result);
            if (dialog.isShowing()) {
                dialog.dismiss();
            }
        }
    }*/

    /**
     * Method to called in LoginActivity to create Intent containing extra info as needed.
     * Helps to hide MainActivity's needed extras
     * @param packageContext current context of application
     * @param first_name user's first name
     * @param last_name user's last name
     * @param reg_num user's registration number
     * @return intent to be created
     */
    public static Intent newIntent(Context packageContext, String first_name, String last_name, String reg_num) {
        Intent i = new Intent(packageContext, MainActivity.class);
        i.putExtra(EXTRA_USER_FIRST_NAME, first_name);
        i.putExtra(EXTRA_USER_LAST_NAME, last_name);
        i.putExtra(EXTRA_USER_REG_NUM, reg_num);
        return i;
    }
}
