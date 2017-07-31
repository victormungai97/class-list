package com.example.android.classlist;

import android.support.v4.app.Fragment;

public class SuggestionActivity extends MainFragmentActivity{

    @Override
    protected Fragment createFragment() {
        return new SuggestionFragment();
    }
}
