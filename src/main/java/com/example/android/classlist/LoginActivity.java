package com.example.android.classlist;

import android.app.ProgressDialog;
import android.content.Intent;
import android.graphics.Color;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Environment;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;

import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.processResults;

public class LoginActivity extends AppCompatActivity {

    Button signInBtn;
    EditText adm_num;
    TextView login_link;
    FloatingActionButton mFloatingActionButton;
    MyTextWatcher regWatcher;
    EditText mServerUrl;
    File directory;

    int status = 0;
    String message;

    private static final String URL_TO_SEND_DATA = "http://192.168.0.11:5000/getstudent/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        if (!Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)){
            Log.e("FOLDER CREATION ERROR","No SDCARD");
        } else {
            directory = new File(Environment.getExternalStorageDirectory() + File.separator
                + "ClassList" + File.separator + "Pictures");
            // if directory does not exist
            if (!directory.isDirectory()) {
                directory.mkdirs(); // create directory and any immediate required directories
            }
        }

        /*
        This is called before initializing the camera because the camera needs permissions(the cause of the crash)
        Also checks for other dangerous permissions like location and phone network
        */
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP ) {
            Permissions.checkPermission(LoginActivity.this, LoginActivity.this);
        }

        login_link = (TextView) findViewById(R.id.login_text);
        signInBtn = (Button) findViewById(R.id.sign_in_btn);
        adm_num = (EditText) findViewById(R.id.admissionNum2);
        mFloatingActionButton = (FloatingActionButton) findViewById(R.id.fab_signin);
        mServerUrl = (EditText) findViewById(R.id.ur_name);

        login_link.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                login_link.setTextColor(Color.rgb(255, 0, 255)); ///
                // Start login activity
                Intent intent = new Intent(LoginActivity.this, RegisterActivity.class);
                // flags to remove current screen after moving to next activity
                intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
            }
        });

        signInBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String reg_no = adm_num.getText().toString();
                String url = mServerUrl.getText().toString();
                try {
                    new SignIn().execute(reg_no,url);
                    if (status == 0) {
                        Toast.makeText(LoginActivity.this, message, Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(LoginActivity.this, message, Toast.LENGTH_SHORT).show();
                    }
                } catch (Exception ex){
                    Log.e(LoginActivity.class.toString(), "Error connecting to main activity.\n" +
                            ex.getMessage());
                }
            }
        });

        mFloatingActionButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(LoginActivity.this, SuggestionActivity.class);
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

        adm_num.addTextChangedListener(regWatcher);
        mServerUrl.setText(URL_TO_SEND_DATA);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("REG_NO",adm_num.getText().toString());
        outState.putString("URL",mServerUrl.getText().toString());
    }

    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        adm_num.setText(savedInstanceState.getString("REG_NO"));
        mServerUrl.setText(savedInstanceState.getString("URL"));
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

    /**
     * Method checks whether information has been entered before submission
     */
    public void updateSubmitButtonState() {
        if (regWatcher.nonEmpty()) {
            signInBtn.setEnabled(true);
        } else {
            signInBtn.setEnabled(false);
        }
    }

    /**
     * Method that connects to next activity
     */
    public void moveToScreen(String ...args){
        String full_name = args[0];
        String reg_no = args[1];
        String dir = args[2];
        Intent intent = MainActivity.newIntent(LoginActivity.this, full_name, reg_no,dir);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }

    private class SignIn extends AsyncTask<String, Void, Void> {

        ProgressDialog progressDialog = new ProgressDialog(LoginActivity.this);

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
            String reg_no = strings[0];
            String url = strings[1];

            Message msg = new Message(reg_no);

            String TAG = "RETRIEVAL SUCCESS ", ERROR = "Retrieval Error: ";
            JSONObject jsonObject;
            jsonObject = processResults(TAG, POST(url,msg), ERROR);
            try {
                status = jsonObject.getInt("STATUS");
                message = jsonObject.getString("MESSAGE");
            } catch (JSONException ex){
                Log.e("JSON error", "Error sending data "+ex.getMessage());
            }

            if (status == 0){
                moveToScreen(message, reg_no,directory.getAbsolutePath());
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
}
