package com.example.android.classlist;

import android.app.ProgressDialog;
import android.content.ContentValues;
import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Color;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.support.annotation.Nullable;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.Fragment;
import android.text.Editable;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.example.android.classlist.database.SignBaseHelper;
import com.example.android.classlist.database.SignInCursorWrapper;
import com.example.android.classlist.database.SignInDbSchema.SignInTable;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.util.ArrayList;

import static com.example.android.classlist.Post.POST;
import static com.example.android.classlist.Post.getContentValues;
import static com.example.android.classlist.Post.processResults;

/**
 * Fragment hosted Login Activity. Will provide UI for user to login
 * Created by User on 7/31/2017.
 */

public class LoginFragment extends Fragment implements Extras {

    Button signInBtn;
    AutoCompleteTextView adm_num;
    TextView login_link;
    FloatingActionButton mFloatingActionButton;
    MyTextWatcher regWatcher;
    EditText mServerUrl;
    File directory;
    SQLiteDatabase mDatabase;

    int status = 0;
    String message;

    private static final String URL_TO_SEND_DATA = "http://192.168.0.11:5000/getstudent/";

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // check if device has external storage memory
        if (!Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)){
            // if no external memory, log error
            Log.e("FOLDER CREATION ERROR","No SDCARD");
        } else {
            directory = new File(Environment.getExternalStorageDirectory() + File.separator
                    + "ClassList" + File.separator + "Pictures");
            // if directory does not exist
            if (!directory.isDirectory()) {
                directory.mkdirs(); // create directory and any immediate required directories
            }
            Log.e("Directory:",""+directory.getAbsolutePath());
        }

        /*
        This is called before initializing the camera because the camera needs permissions(the cause of the crash)
        Also checks for other dangerous permissions like location and phone network
        */
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP ) {
            Permissions.checkPermission(getActivity(), getActivity());
        }
    }

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_login,container,false);

        // initialize widgets
        login_link = (TextView) view.findViewById(R.id.login_text);
        signInBtn = (Button) view.findViewById(R.id.sign_in_btn);
        mFloatingActionButton = (FloatingActionButton) view.findViewById(R.id.fab_signin);
        mServerUrl = (EditText) view.findViewById(R.id.ur_name);
        mDatabase = new SignBaseHelper(getActivity()).getWritableDatabase();

        adm_num = (AutoCompleteTextView) view.findViewById(R.id.admissionNum2);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(getActivity(),
                android.R.layout.simple_dropdown_item_1line, getRegnos());
        adm_num.setAdapter(adapter);

        login_link.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                login_link.setTextColor(Color.rgb(255, 0, 255)); // set color to magenta
                // Start login activity
                Intent intent = new Intent(getActivity(), RegisterActivity.class);
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
                        Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show();
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
                Intent intent = new Intent(getActivity(), SuggestionActivity.class);
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

        return view;
    }

    @Override
    public void moveToScreen(String ...args){
        String full_name = args[0];
        String reg_no = args[1];
        String dir = args[2];

        // save data to SQLite database
        ContentValues values = getContentValues(reg_no,full_name);
        mDatabase.insert(SignInTable.NAME, null, values); // insert(table_name, null, contentValues)

        Intent intent = MainActivity.newIntent(getActivity(), full_name, reg_no, dir);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }

    /**
     * Gets list of registration numbers for auto completion from database
     * @return list of registration numbers
     */
    public ArrayList<String> getRegnos() {
        // create array list to hold saved registration numbers
        ArrayList<String> reg_nos = new ArrayList<>();
        // create wrapper for cursor
        SignInCursorWrapper cursor = queryRegno(null, null);

        // get received reg. nos. and add to array list
        try {
            cursor.moveToFirst();
            while (!cursor.isAfterLast()) {
                reg_nos.add(cursor.getRegNo());
                cursor.moveToNext();
            }
        } finally {
            cursor.close();
        }
        return reg_nos;
    }

    /**
     * Creates the query for retrieving registration numbers
     * @param whereClause where statement
     * @param whereArgs condition(s)
     * @return instance of cursor wrapper
     */
    private SignInCursorWrapper queryRegno(String whereClause, String[] whereArgs) {
        Cursor cursor = mDatabase.query(
                SignInTable.NAME, // Table
                new String[]{ SignInTable.Cols.REG_NO }, // Columns - null selects all columns
                whereClause, // WHERE
                whereArgs, // Conditions to be met
                null, // groupBy
                null, // having
                null // orderBy
        );
        return new SignInCursorWrapper(cursor);
    }

    @Override
    public void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("REG_NO",adm_num.getText().toString());
        outState.putString("URL",mServerUrl.getText().toString());
    }

    @Override
    public void onActivityCreated(Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);

        if (savedInstanceState != null) {
            adm_num.setText(savedInstanceState.getString("REG_NO"));
            mServerUrl.setText(savedInstanceState.getString("URL"));
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
