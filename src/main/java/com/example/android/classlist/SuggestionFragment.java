package com.example.android.classlist;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.processResults;

/**
 * Fragment for the Suggestions Activity. It will provide interface for users to input suggestions
 * Created by User on 7/30/2017.
 */

public class SuggestionFragment extends Fragment implements AdapterView.OnItemSelectedListener
        , Extras, View.OnClickListener{
    private EditText mEditText;
    private FloatingActionButton fab;
    private EditText mServerUrl;

    Spinner spinner;
    String choice;
    String message;
    Integer status;

    private static final String URL_TO_SEND_DATA = "http://192.168.0.11:5000/suggestions/";

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_suggestion, container, false);

        mEditText = (EditText) view.findViewById(R.id.editText);
        spinner = (Spinner) view.findViewById(R.id.spinner1);
        spinner.setOnItemSelectedListener(this);
        fab = (FloatingActionButton) view.findViewById(R.id.fab_send);
        mServerUrl = (EditText) view.findViewById(R.id.suggest_ur);
        mServerUrl.setText(URL_TO_SEND_DATA);

        if (mServerUrl.toString().length() == 0)
            fab.setEnabled(false);

        fab.setOnClickListener(this);

        return view;
    }

    @Override
    public void moveToScreen(String ...args){
        Intent intent = new Intent(getActivity(),LoginActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }

    @Override
    public void onItemSelected(AdapterView<?> adapterView, View view, int position, long id) {
        // On selecting a spinner item
        choice = adapterView.getItemAtPosition(position).toString();
        mEditText.setEnabled(true);
        fab.setEnabled(true);

        Toast.makeText(getActivity(),"Selected "+choice,Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {
        // if no message selected
        mEditText.setEnabled(false);
        fab.setEnabled(false);
    }

    @Override
    public void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("MESSAGE",mEditText.getText().toString());
        outState.putString("URL",mServerUrl.getText().toString());
        outState.putString("CHOICE",choice);
    }

    @Override
    public void onActivityCreated(Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);

        if (savedInstanceState != null) {
            mEditText.setText(savedInstanceState.getString("MESSAGE"));
            mServerUrl.setText(savedInstanceState.getString("URL"));
            spinner.setPrompt(savedInstanceState.getCharSequence("CHOICE"));
        }
    }

    @Override
    public void onClick (View v){
        message = mEditText.getText().toString();
        Message msg = new Message();
        msg.setMessage(message);
        msg.setChoice(choice);
        try{
            new SendSuggestion().execute(msg);
            if (status == 0) {
                Toast.makeText(getActivity(), "Suggestion sent", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show();
            }
        } catch (Exception ex){
            Log.e(SuggestionActivity.class.toString(), "Error sending suggestion "+ex.getMessage());
        }
    }

    private class SendSuggestion extends AsyncTask<Message, Void, Void> {
        ProgressDialog progressDialog = new ProgressDialog(getActivity());
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

    /*
     * A LITTLE SOMETHING
     * John 1:3 - Through him all things were made; without him, nothing was made that has been made.
     */
}
