package com.example.android.classlist;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.os.Handler;

public class SplashScreenActivity extends AppCompatActivity {

    // time for splash screen to last in milliseconds
    private static final long SPLASH_TIME = 3000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash_screen);

        new Handler().postDelayed(new Runnable() {

            /*
            * Showing splash screen with given run time.
             */
            @Override
            public void run() {
                // Method will run once splash time is over
                // Start login activity
                Intent intent = new Intent(SplashScreenActivity.this, LoginActivity.class);
                // flags to remove current screen after moving to next activity
                intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);

                finish(); // close this activity
            }
        }, SPLASH_TIME);
    }
}
