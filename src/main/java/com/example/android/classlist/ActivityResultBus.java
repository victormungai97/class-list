package com.example.android.classlist;

import android.os.Handler;
import android.os.Looper;

import com.squareup.otto.Bus;

/**
 * Created by User on 7/31/2017.
 * Class is a singleton of Event Bus which will be used to send a package from an Activity
 * to all of active Fragments.
 */
class ActivityResultBus extends Bus {

    private static ActivityResultBus instance;

    static ActivityResultBus getInstance() {
        if (instance == null)
            instance = new ActivityResultBus();
        return instance;
    }

    private Handler mHandler = new Handler(Looper.getMainLooper());

    /**
     * used to send a package into the bus
     * @param obj Any Java Object
     */
    void postQueue(final Object obj) {
        // delay package sending to allow Fragment to become active
        mHandler.post(new Runnable() {
            @Override
            public void run() {
                ActivityResultBus.getInstance().post(obj);
            }
        });
    }

}
