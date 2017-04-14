package com.example.android.classlist;

import android.content.Intent;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

public class SuggestionActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener{

    private EditText mEditText;
    private Spinner spinner;
    private FloatingActionButton fab;

    String choice;
    String message;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_suggestion);

        mEditText = (EditText) findViewById(R.id.editText);
        spinner = (Spinner) findViewById(R.id.spinner1);
        spinner.setOnItemSelectedListener(this);
        fab = (FloatingActionButton) findViewById(R.id.fab_send);
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

    public void sendMessage(View v){
        message = mEditText.getText().toString();

        Toast.makeText(this,"Message selected",Toast.LENGTH_SHORT).show();
        Intent intent = new Intent(SuggestionActivity.this,LoginActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }
}
