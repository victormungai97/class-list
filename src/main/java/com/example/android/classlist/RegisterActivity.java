package com.example.android.classlist;

import android.content.Intent;
import android.support.v4.app.Fragment;

public class RegisterActivity extends MainFragmentActivity{
    @Override
    protected Fragment createFragment() {
        return new RegisterFragment();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        ActivityResultBus.getInstance().postQueue(
                new ActivityResultEvent(requestCode, resultCode, data));
    }
}
