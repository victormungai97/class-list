package com.example.android.classlist;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.processResults;

public class SuggestionActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener
                , Extras{

    private EditText mEditText;
    private FloatingActionButton fab;
    private EditText mServerUrl;

    Spinner spinner;
    String choice;
    String message;
    Integer status;

    private static final String URL_TO_SEND_DATA = "http://192.168.0.11:5000/suggestions/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_suggestion);

        mEditText = (EditText) findViewById(R.id.editText);
        spinner = (Spinner) findViewById(R.id.spinner1);
        spinner.setOnItemSelectedListener(this);
        fab = (FloatingActionButton) findViewById(R.id.fab_send);
        mServerUrl = (EditText) findViewById(R.id.suggest_ur);
        mServerUrl.setText(URL_TO_SEND_DATA);

        if (mServerUrl.toString().length() == 0)
            fab.setEnabled(false);
    }

    @Override
    public void onItemSelected(AdapterView<?> adapterView, View view, int position, long id) {
        // On selecting a spinner item
        choice = adapterView.getItemAtPosition(position).toString();
        mEditText.setEnabled(true);
        fab.setEnabled(true);

        Toast.makeText(this,"Selected "+choice,Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {
        // if no message selected
        mEditText.setEnabled(false);
        fab.setEnabled(false);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("MESSAGE",mEditText.getText().toString());
        outState.putString("URL",mServerUrl.getText().toString());
        outState.putString("CHOICE",choice);
    }

    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        mEditText.setText(savedInstanceState.getString("MESSAGE"));
        mServerUrl.setText(savedInstanceState.getString("URL"));
        spinner.setPrompt(savedInstanceState.getCharSequence("CHOICE"));
    }

    public void sendMessage(View v){
        message = mEditText.getText().toString();
        Message msg = new Message();
        msg.setMessage(message);
        msg.setChoice(choice);
        try{
            new SendSuggestion().execute(msg);
            if (status == 0) {
                Toast.makeText(SuggestionActivity.this, "Suggestion sent", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(SuggestionActivity.this, message, Toast.LENGTH_SHORT).show();
            }
        } catch (Exception ex){
            Log.e(SuggestionActivity.class.toString(), "Error sending suggestion "+ex.getMessage());
        }
    }

    @Override
    public void moveToScreen(String ...args){
        Intent intent = new Intent(SuggestionActivity.this,LoginActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }

    private class SendSuggestion extends AsyncTask<Message, Void, Void>{
        ProgressDialog progressDialog = new ProgressDialog(SuggestionActivity.this);
        String url = mServerUrl.getText().toString();

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            progressDialog.setMessage("Please wait");
            progressDialog.setIndeterminate(true);
            progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            progressDialog.show();
        }


        @Override
        protected Void doInBackground(Message... messages) {
            Message msg = messages[0];

            String TAG = "SUGGESTION SUCCESS ", ERROR = "Suggestion Error: ";
            JSONObject jsonObject;
            jsonObject = processResults(TAG, POST(url,msg), ERROR);
            try {
                status = jsonObject.getInt("STATUS");
                message = jsonObject.getString("MESSAGE");
            } catch (JSONException ex){
                Log.e("JSON error", "Error sending data "+ex.getMessage());
            }

            if (status == 0) {
                moveToScreen(message);
            } else {
                message = "Connection unsuccessful. Suggestion not sent.";
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
