package com.example.android.classlist;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Build;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.processResults;

public class RegisterActivity extends AppCompatActivity {

    private EditText first_name;
    private EditText last_name;
    private EditText admission_num;
    private Button mSignInButton;
    EditText mServerUrl;
    private FloatingActionButton fab;

    private static final String URL_TO_SEND_DATA = "http://192.168.0.11:5000/registration/";

    MyTextWatcher firstNameWatcher;
    MyTextWatcher regWatcher;
    MyTextWatcher lastNameWatcher;

    int status = 0;
    String message;

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
        fab = (FloatingActionButton) findViewById(R.id.fab);
        mServerUrl = (EditText) findViewById(R.id.ur_name_register);

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
                if (editable.toString().length() == 0) {
                    empty = true;
                } else {
                    empty = false;
                }
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
                if (editable.toString().length() == 0) {
                    empty = true;
                } else {
                    empty = false;
                }
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
                if (editable.toString().length() == 0) {
                    empty = true;
                } else {
                    empty = false;
                }
                updateSubmitButtonState();
            }
        };

        first_name.addTextChangedListener(firstNameWatcher);
        last_name.addTextChangedListener(lastNameWatcher);
        admission_num.addTextChangedListener(regWatcher);
        mServerUrl.setText(URL_TO_SEND_DATA);

        mSignInButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String firstname = first_name.getText().toString(),
                        lastname = last_name.getText().toString(),
                        reg_no = admission_num.getText().toString();
                String url = mServerUrl.getText().toString();
                try {
                    new SignIn().execute(firstname, lastname, reg_no, url);
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
        outState.putString("FIRST NAME",first_name.getText().toString());
        outState.putString("LAST NAME",last_name.getText().toString());
        outState.putString("REG_NO",admission_num.getText().toString());
        outState.putString("URL",mServerUrl.getText().toString());
    }

    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        first_name.setText(savedInstanceState.getString("FIRST NAME"));
        last_name.setText(savedInstanceState.getString("LAST NAME"));
        admission_num.setText(savedInstanceState.getString("REG_NO"));
        mServerUrl.setText(savedInstanceState.getString("URL"));
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

    /**
     * Method checks whether information has been entered before submission
     */
    public void updateSubmitButtonState() {
        if ( firstNameWatcher.nonEmpty() && regWatcher.nonEmpty() && lastNameWatcher.nonEmpty() ) {
            mSignInButton.setEnabled(true);
        } else {
            mSignInButton.setEnabled(false);
        }
    }

    public class SignIn extends AsyncTask<String, Void, Void>{

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

            Message msg = new Message(name, reg_no);

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

   void moveToScreen() {
        Intent intent = new Intent(RegisterActivity.this, LoginActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }
}
