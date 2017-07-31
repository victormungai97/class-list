package com.example.android.classlist;

import android.content.ContentValues;
import android.util.Log;

import com.example.android.classlist.database.SignInDbSchema.SignInTable;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

/**
 * Created by User on 4/28/2017.
 * Class contains methods for connection to database
 * POST posts message to url, processResults processes the post's results and
 * contentValues creates a key-value pair for insertion into SQLite database
 */

class Post {

    // json keys
    private static final String NAME = "name";
    private static final String REG_NO = "regno";
    private static final String PIC = "picture";
    private static final String TIME = "time";
    private static final String LATITUDE = "latitude";
    private static final String LONGITUDE = "longitude";
    private static final String LAC = "lac";
    private static final String CI = "ci";
    private static final String PHONE = "phone";
    private static final String SUGGESTION = "suggestion";
    private static final String CHOICE = "choice";

    /**
     * Open Http connection.
     * Create HttpPOST object passing the url.
     * Create Person object & convert it to JSON string.
     * Add JSON to HttpPOST, set headers & send the POST request.
     * Get the response Inputstream, convert it to String and return it.
     * @param  url URL to send to
     * @param message message to be sent
     * @return response as String
     */
    static String POST(String url, Message message){
        InputStream inputStream;
        String result = "";
        try {

            // create HttpClient
            HttpClient httpclient = new DefaultHttpClient();

            // make POST request to the given URL
            HttpPost httpPost = new HttpPost(url);

            String json;

            // build jsonObject
            JSONObject jsonObject = new JSONObject();
            jsonObject.accumulate(NAME, message.getName());
            jsonObject.accumulate(REG_NO, message.getReg_no());
            jsonObject.accumulate(TIME, message.getTime());
            jsonObject.accumulate(PIC, message.getPic());
            jsonObject.accumulate(LATITUDE,message.getLatitude());
            jsonObject.accumulate(LONGITUDE, message.getLongitude());
            jsonObject.accumulate(LAC, message.getLac());
            jsonObject.accumulate(CI, message.getCi());
            jsonObject.accumulate(PHONE, message.getPhone());
            jsonObject.accumulate(SUGGESTION,message.getMessage());
            jsonObject.accumulate(CHOICE, message.getChoice());

            // convert JSONObject to JSON to String
            json = jsonObject.toString();

            // ** Alternative way to convert Message object to JSON string usin Jackson Lib
            // ObjectMapper mapper = new ObjectMapper();
            // json = mapper.writeValueAsString(message);

            // set json to StringEntity
            StringEntity se = new StringEntity(json);

            // set httpPost Entity
            httpPost.setEntity(se);

            // Set some headers to inform server about the type of the content
            httpPost.setHeader("Accept", "application/json");
            httpPost.setHeader("Content-type", "application/json");

            // Execute POST request to the given URL
            HttpResponse httpResponse = httpclient.execute(httpPost);

            // receive response as inputStream
            inputStream = httpResponse.getEntity().getContent();

            // convert inputstream to string
            if(inputStream != null)
                result = convertInputStreamToString(inputStream);
            else
                result = "Did not work!";

        } catch (Exception e) {
            Log.d("InputStream", e.getLocalizedMessage());
        }

        // 11. return result
        return result;
    }


    /**
     * Helper method to convert input stream to String
     * @param inputStream inputStream to be converted
     * @return String
     * @throws IOException exception opening reader
     */

    private static String convertInputStreamToString(InputStream inputStream) throws IOException {
        BufferedReader bufferedReader = new BufferedReader( new InputStreamReader(inputStream));
        String line;
        String result = "";
        while((line = bufferedReader.readLine()) != null)
            result += line;

        inputStream.close();
        return result;

    }

    /**
     * Method to process response from server
     * @param TAG tag for successful communication
     * @param response response to be analysed
     * @param ERROR tag for unsuccessful communication
     * @return JSON object containing results of processing
     */
    static JSONObject processResults(String TAG, String response, String ERROR){
        JSONObject jsonObject = new JSONObject();
        int status;
        String message;

        // log response
        Log.d("Create Request: ", "> " + response);

        try {
            if (response != null) {
                try {
                    // convert string to json object
                    JSONObject jsonObj = new JSONObject(response);
                    boolean error = jsonObj.getBoolean("error");
                    // checking for error node in json
                    if (!error) {
                        // new category created successfully
                        status = 0;
                        Log.i(TAG,
                                "> " + jsonObj.getString("message"));
                        message = jsonObj.getString("message");
                    } else {
                        status = 1;
                        Log.e(ERROR,
                                "> " + jsonObj.getString("message"));
                        message = jsonObj.getString("message");
                    }

                } catch (JSONException e) {
                    status = 2;
                    e.printStackTrace();
                    message = "Error sending data";
                }

            } else {
                status = 3;
                Log.e("JSON Data", "JSON data error!");
                message = "Error sending data";
            }

            jsonObject.accumulate("STATUS", status);
            jsonObject.accumulate("MESSAGE", message);
        } catch (JSONException ex){
            Log.e("JSON error", "Error sending data "+ex.getMessage());
        }

        return jsonObject;
    }

    /**
     * Method that maps student's details to their respective columns
     * @param reg_no Student's registration number
     * @param name Student's name
     * @return content value containing column names and their values
     */
    static ContentValues getContentValues(String reg_no, String name) {
        ContentValues values = new ContentValues();
        values.put(SignInTable.Cols.REG_NO, reg_no);
        values.put(SignInTable.Cols.NAME, name);
        return values;
    }
}
