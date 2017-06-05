package com.example.android.classlist;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.ContentValues;
import android.content.Intent;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Bitmap;
import android.graphics.drawable.BitmapDrawable;
import android.media.FaceDetector;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.Toast;

import com.example.android.classlist.database.SignBaseHelper;
import com.example.android.classlist.database.SignInDbSchema.SignInTable;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.getContentValues;
import static com.example.android.classlist.Post.processResults;

public class RegisterActivity extends AppCompatActivity implements Extras{

    private EditText first_name;
    private EditText last_name;
    private EditText admission_num;
    private Button mSignInButton;
    private ImageView mImageView;
    private Uri imageForUpload;
    private String mCurrentPhotoPath;
    EditText mServerUrl;
    FloatingActionButton fab;
    private ImageButton mImageButton;

    private static final String URL_TO_SEND_DATA = "http://192.168.0.11:5000/registration/";
    private static final int REQUEST_PHOTO = 1;
    private static final String TAG = "RegisterActivity";

    Bitmap photo;
    MyTextWatcher firstNameWatcher;
    MyTextWatcher regWatcher;
    MyTextWatcher lastNameWatcher;

    int status = 0;
    String message;
    SQLiteDatabase mDatabase;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP){
            Permissions.checkPermission(RegisterActivity.this, RegisterActivity.this);
        }

        first_name = (EditText) findViewById(R.id.firstName);
        last_name = (EditText) findViewById(R.id.lastName);
        admission_num = (EditText) findViewById(R.id.admissionNum);
        mSignInButton = (Button) findViewById(R.id.register_btn);
        mImageView = (ImageView) findViewById(R.id.register_photo);
        fab = (FloatingActionButton) findViewById(R.id.fab);
        mServerUrl = (EditText) findViewById(R.id.ur_name_register);
        mImageButton = (ImageButton) findViewById(R.id.register_photo_btn);
        mDatabase = new SignBaseHelper(getApplicationContext()).getWritableDatabase();

        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(RegisterActivity.this, SuggestionActivity.class);
                startActivity(intent);
            }
        });

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

        firstNameWatcher = new MyTextWatcher() {
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

        lastNameWatcher = new MyTextWatcher() {
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

        first_name.addTextChangedListener(firstNameWatcher);
        last_name.addTextChangedListener(lastNameWatcher);
        admission_num.addTextChangedListener(regWatcher);
        mServerUrl.setText(URL_TO_SEND_DATA);

        mImageButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                takePicture();
                galleryAddPic();
            }
        });

        mImageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                takePicture();
                galleryAddPic();
            }
        });

        mSignInButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String firstname = first_name.getText().toString(),
                        lastname = last_name.getText().toString(),
                        reg_no = admission_num.getText().toString();
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                photo.compress(Bitmap.CompressFormat.JPEG, 100, baos); //bm is the bitmap object
                byte[] byteArrayImage = baos.toByteArray();
                String image = Base64.encodeToString(byteArrayImage, Base64.DEFAULT);
                String url = mServerUrl.getText().toString();
                try {
                    new SignIn().execute(firstname, lastname, reg_no, url, image);
                    if (status == 0) {
                        Toast.makeText(RegisterActivity.this, "Successful registration", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(RegisterActivity.this, message, Toast.LENGTH_SHORT).show();
                    }
                } catch (Exception ex){
                    Log.e(RegisterActivity.class.toString(), "Error connecting to main activity\n"+
                        ex.getMessage());
                }
            }
        });
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putParcelable("photo",photo);
        outState.putString("FIRST NAME",first_name.getText().toString());
        outState.putString("LAST NAME",last_name.getText().toString());
        outState.putString("REG_NO",admission_num.getText().toString());
        outState.putString("URL",mServerUrl.getText().toString());
    }

    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        photo = savedInstanceState.getParcelable("photo");
        first_name.setText(savedInstanceState.getString("FIRST NAME"));
        last_name.setText(savedInstanceState.getString("LAST NAME"));
        admission_num.setText(savedInstanceState.getString("REG_NO"));
        mServerUrl.setText(savedInstanceState.getString("URL"));
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
     * Method returns the file containing the photo
     * @return photo file
     */
    public File getPhotoFile() {
        File externalFilesDir;
        externalFilesDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);

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
        DateFormat df = new SimpleDateFormat("ddMMyyyy_hhmmssSSS", Locale.ROOT);
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
     * Method checks whether information has been entered before submission
     */
    public void updateSubmitButtonState() {
        if ( photo != null && firstNameWatcher.nonEmpty() && regWatcher.nonEmpty() && lastNameWatcher.nonEmpty() ) {
            mSignInButton.setEnabled(true);
        } else {
            mSignInButton.setEnabled(false);
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
                    photo = PictureUtilities.getScaledBitmap(imageForUpload.getPath(),RegisterActivity.this);

                    if (photo != null) {
                        // detect only one face to set to image view
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

    private class SignIn extends AsyncTask<String, Void, Void>{

        ProgressDialog progressDialog = new ProgressDialog(RegisterActivity.this);

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            progressDialog.setMessage("Please wait");
            progressDialog.setIndeterminate(true);
            progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            progressDialog.show();
        }

        @Override
        protected Void doInBackground(String... strings) {
            String first_name = strings[0];
            String last_name = strings[1];
            String reg_no = strings[2];
            String name = first_name + " " + last_name;
            String url = strings[3];
            String img = strings[4];

            Message msg = new Message(name, reg_no);
            msg.setPic(img);

            String TAG = "REGISTRATION SUCCESS ", ERROR = "Registration Error: ";
            JSONObject jsonObject;
            jsonObject = processResults(TAG, POST(url,msg), ERROR);
            try {
                status = jsonObject.getInt("STATUS");
                message = jsonObject.getString("MESSAGE");
            } catch (JSONException ex){
                Log.e("JSON error", "Error sending data "+ex.getMessage());
            }

            if (status == 0){
                ContentValues values = getContentValues(reg_no,name);
                mDatabase.insert(SignInTable.NAME, null, values);
                moveToScreen();
            }

            return null;
        }

        @Override
        protected void onPostExecute(Void aVoid) {
            super.onPostExecute(aVoid);
            if (progressDialog.isShowing()){
                progressDialog.cancel();
            }
        }
    }

    @Override
    public void moveToScreen(String ...args) {
        Intent intent = new Intent(RegisterActivity.this, LoginActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }
}
