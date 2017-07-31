package com.example.android.classlist;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.ContentValues;
import android.content.Intent;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.Fragment;
import android.text.Editable;
import android.util.Base64;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.Toast;

import com.example.android.classlist.database.SignBaseHelper;
import com.example.android.classlist.database.SignInDbSchema.SignInTable;
import com.squareup.otto.Subscribe;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;

import static com.example.android.classlist.PictureUtilities.galleryAddPic;
import static com.example.android.classlist.PictureUtilities.recogniseFace;
import static com.example.android.classlist.PictureUtilities.takePicture;
import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.getContentValues;
import static com.example.android.classlist.Post.processResults;

/**
 * Fragment hosted by Register Activity. Allows user to register to the attendance system.
 * Created by User on 7/31/2017.
 */

public class RegisterFragment extends Fragment implements Extras{

    private EditText first_name;
    private EditText last_name;
    private EditText admission_num;
    private Button mSignInButton;
    private ImageView mImageView;
    private Uri imageForUpload;
    EditText mServerUrl;
    FloatingActionButton fab;
    ImageButton mImageButton;

    private static final String URL_TO_SEND_DATA = "http://192.168.0.11:5000/registration/";
    private static final int REQUEST_PHOTO = 14563;
    private static final String TAG = "RegisterActivity";

    Bitmap photo;
    Extras.MyTextWatcher firstNameWatcher;
    Extras.MyTextWatcher regWatcher;
    Extras.MyTextWatcher lastNameWatcher;

    int status = 0;
    String message;
    SQLiteDatabase mDatabase;

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // check and request any permissions not granted
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP){
            Permissions.checkPermission(getActivity(), getActivity());
        }
    }

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_register,container,false);

        // initialize widgets
        first_name = (EditText) view.findViewById(R.id.firstName);
        last_name = (EditText) view.findViewById(R.id.lastName);
        admission_num = (EditText) view.findViewById(R.id.admissionNum);
        mSignInButton = (Button) view.findViewById(R.id.register_btn);
        mImageView = (ImageView) view.findViewById(R.id.register_photo);
        fab = (FloatingActionButton) view.findViewById(R.id.fab);
        mServerUrl = (EditText) view.findViewById(R.id.ur_name_register);
        mImageButton = (ImageButton) view.findViewById(R.id.register_photo_btn);
        mDatabase = new SignBaseHelper(getActivity()).getWritableDatabase();

        // redirect to suggestion activity
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(getActivity(), SuggestionActivity.class);
                startActivity(intent);
            }
        });

        // listen to typing of edit text
        regWatcher = new Extras.MyTextWatcher() {
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

        firstNameWatcher = new Extras.MyTextWatcher() {
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

        lastNameWatcher = new Extras.MyTextWatcher() {
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

        // set text watchers to respective edit texts
        first_name.addTextChangedListener(firstNameWatcher);
        last_name.addTextChangedListener(lastNameWatcher);
        admission_num.addTextChangedListener(regWatcher);
        mServerUrl.setText(URL_TO_SEND_DATA);

        // check if button is present before continuing
        if (mImageButton != null) {
            // take picture by clicking button
            mImageButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    imageForUpload = takePicture(getActivity(), TAG);
                    galleryAddPic(getActivity());
                }
            });
        }

        // take picture by clicking image view
        mImageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                imageForUpload = takePicture(getActivity(), TAG);
                galleryAddPic(getActivity());
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
                        Toast.makeText(getActivity(), "Successful registration", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show();
                    }
                } catch (Exception ex){
                    Log.e(RegisterActivity.class.toString(), "Error connecting to main activity\n"+
                            ex.getMessage());
                }
            }
        });

        return view;
    }

    /**
     * Method retrieves image sent by return intent as small Bitmap in extras with data as key
     * and displays to ImageView
     * @param requestCode request that was received from take picture
     * @param resultCode result of operation
     * @param data return intent
     */
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode,resultCode,data);
        try {
            if (requestCode == REQUEST_PHOTO && resultCode == Activity.RESULT_OK) {
                if (imageForUpload != null) {
                    photo = recogniseFace(imageForUpload, mImageView, getActivity());
                    updateSubmitButtonState();
                } else {
                    Toast.makeText(getActivity(),"Error2 while capturing image",Toast.LENGTH_SHORT).show();
                }
            }
        } catch (Exception ex) {
            Log.e("BITMAP error",ex.getMessage());
        }
    }

    @Override
    public void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putParcelable("photo",photo);
        outState.putString("FIRST NAME",first_name.getText().toString());
        outState.putString("LAST NAME",last_name.getText().toString());
        outState.putString("REG_NO",admission_num.getText().toString());
        outState.putString("URL",mServerUrl.getText().toString());
    }

    @Override
    public void onActivityCreated(Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);

        // retrieve contents on screen before rotation
        if (savedInstanceState != null) {
            photo = savedInstanceState.getParcelable("photo");
            first_name.setText(savedInstanceState.getString("FIRST NAME"));
            last_name.setText(savedInstanceState.getString("LAST NAME"));
            admission_num.setText(savedInstanceState.getString("REG_NO"));
            mServerUrl.setText(savedInstanceState.getString("URL"));
        }
    }

    @Override
    public void onStart() {
        super.onStart();
        ActivityResultBus.getInstance().register(mActivityResultSubscriber);
    }

    @Override
    public void onStop() {
        super.onStop();
        ActivityResultBus.getInstance().unregister(mActivityResultSubscriber);
    }

    // facilitates creation of brodcasts so as to pass activity result from activity to fragment
    private Object mActivityResultSubscriber = new Object() {
        @Subscribe
        public void onActivityResultReceived(ActivityResultEvent event) {
            int requestCode = event.getRequestCode();
            int resultCode = event.getResultCode();
            Intent data = event.getData();
            onActivityResult(requestCode, resultCode, data);
        }
    };

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

    private class SignIn extends AsyncTask<String, Void, Void> {

        ProgressDialog progressDialog = new ProgressDialog(getActivity());

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
        Intent intent = new Intent(getActivity(), LoginActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }
}
