package com.example.android.classlist;

/**
 * Created by User on 4/22/2017.
 */

public class Message {
    private String name="";
    private String reg_no="";
    private String time="";
    private String pic="";
    private String latitude="";
    private String longitude="";
    private String lac="";
    private String ci="";

    public Message(String name, String reg_no, String time, String pic, String latitude, String longitude, String lac, String ci) {
        this.name = name;
        this.reg_no = reg_no;
        this.time = time;
        this.pic = pic;
        this.latitude = latitude;
        this.longitude = longitude;
        this.lac = lac;
        this.ci = ci;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getReg_no() {
        return reg_no;
    }

    public void setReg_no(String reg_no) {
        this.reg_no = reg_no;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

    public String getPic() {
        return pic;
    }

    public void setPic(String pic) {
        this.pic = pic;
    }

    public String getLatitude() {
        return latitude;
    }

    public void setLatitude(String latitude) {
        this.latitude = latitude;
    }

    public String getLongitude() {
        return longitude;
    }

    public void setLongitude(String longitude) {
        this.longitude = longitude;
    }

    public String getLac() {
        return lac;
    }

    public void setLac(String lac) {
        this.lac = lac;
    }

    public String getCi() {
        return ci;
    }

    public void setCi(String ci) {
        this.ci = ci;
    }
}
