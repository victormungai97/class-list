package com.example.android.classlist;

import android.Manifest;
import android.app.ProgressDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.AsyncTask;
import android.os.Build;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

public class LoginActivity extends AppCompatActivity {

    private EditText first_name;
    private EditText last_name;
    private EditText admission_num;
    private Button mSignInButton;
    private FloatingActionButton fab;

    MyTextWatcher firstNameWatcher;
    MyTextWatcher regWatcher;
    MyTextWatcher lastNameWatcher;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP){
            Permissions.checkPermission(LoginActivity.this, LoginActivity.this);
        }

        first_name = (EditText) findViewById(R.id.firstName);
        last_name = (EditText) findViewById(R.id.lastName);
        admission_num = (EditText) findViewById(R.id.admissionNum);
        mSignInButton = (Button) findViewById(R.id.sign_in_btn);
        fab = (FloatingActionButton) findViewById(R.id.fab);

        fab.setOnClickListener(new View.OnClickListener() {
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

        mSignInButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String firstname = first_name.getText().toString(),
                        lastname = last_name.getText().toString(),
                        reg_no = admission_num.getText().toString();
                Log.e(LoginActivity.class.toString(), "Error connecting to main activity");
                new SignIn().execute(firstname, lastname, reg_no);
            }
        });
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("FIRST NAME",first_name.getText().toString());
        outState.putString("LAST NAME",last_name.getText().toString());
        outState.putString("REG_NO",admission_num.getText().toString());
    }

    /**
     * Method that connects to next activity
     */
    public void moveToScreen(String ...args){
        String first_name = args[0];
        String last_name = args[1];
        String reg_no = args[2];
        Intent intent = MainActivity.newIntent(LoginActivity.this, first_name, last_name, reg_no);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }

    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        first_name.setText(savedInstanceState.getString("FIRST NAME"));
        last_name.setText(savedInstanceState.getString("LAST NAME"));
        admission_num.setText(savedInstanceState.getString("REG_NO"));
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
            moveToScreen(strings);
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
