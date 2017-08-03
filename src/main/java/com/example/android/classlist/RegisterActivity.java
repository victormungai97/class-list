package com.example.android.classlist;

import android.support.v4.app.Fragment;

public class RegisterActivity extends MainFragmentActivity{
    @Override
    protected Fragment createFragment() {
        return new RegisterFragment();
    }
}
