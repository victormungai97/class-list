package com.example.android.classlist;

import android.content.Context;
import android.content.Intent;
import android.support.v4.app.Fragment;

public class MainActivity extends MainFragmentActivity{

    private static final String EXTRA_USER_FULL_NAME = "com.example.android.classlist.full_name";
    private static final String EXTRA_USER_REG_NUM = "com.example.android.classlist.reg_num";
    private static final String EXTRA_USER_DIR = "com.example.android.classlist.directory";

    /**
     * Method to called in RegisterActivity to create Intent containing extra info as needed.
     * Helps to hide MainActivity's needed extras
     * @param packageContext current context of application
     * @param full_name user's full name
     * @param reg_num user's registration number
     * @return intent to be created
     */
    public static Intent newIntent(Context packageContext, String full_name, String reg_num,
                                   String dir) {
        Intent i = new Intent(packageContext, MainActivity.class);
        i.putExtra(EXTRA_USER_FULL_NAME, full_name);
        i.putExtra(EXTRA_USER_REG_NUM, reg_num);
        i.putExtra(EXTRA_USER_DIR, dir);
        return i;
    }

    @Override
    protected Fragment createFragment(){
        // retrieve saved key-value intent pair and pass to fragment
        String name = getIntent().getStringExtra(EXTRA_USER_FULL_NAME);
        String reg_num = getIntent().getStringExtra(EXTRA_USER_REG_NUM);
        String dir = getIntent().getStringExtra(EXTRA_USER_DIR);
        return MainFragment.newInstance(name,reg_num,dir);
    }
}
