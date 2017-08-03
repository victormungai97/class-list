package com.example.android.classlist;

import android.content.Intent;

/**
 * Created by User on 7/31/2017
 * Class creates a bus event as a package carry Activity Result values.
 */
class ActivityResultEvent {

    private int requestCode;
    private int resultCode;
    private Intent data;

    ActivityResultEvent(int requestCode, int resultCode, Intent data) {
        this.requestCode = requestCode;
        this.resultCode = resultCode;
        this.data = data;
    }

    int getRequestCode() {
        return requestCode;
    }

    public void setRequestCode(int requestCode) {
        this.requestCode = requestCode;
    }

    int getResultCode() {
        return resultCode;
    }

    void setResultCode(int resultCode) {
        this.resultCode = resultCode;
    }

    public Intent getData() {
        return data;
    }

    public void setData(Intent data) {
        this.data = data;
    }
}
