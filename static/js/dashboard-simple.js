// Simple test version
console.log('✅ JavaScript loaded!');

window.addEventListener('load', function() {
    console.log('✅ Window loaded!');

    const btn = document.getElementById('runScanBtn');
    console.log('🔍 Button found:', btn);

    if (btn) {
        btn.addEventListener('click', function() {
            alert('Button clicked! This works.');
            console.log('🎯 Button clicked!');

            fetch('/api/scan')
                .then(r => {
                    console.log('Response:', r.status);
                    return r.json();
                })
                .then(data => {
                    console.log('Data:', data);
                    alert('Scan complete! Compliance: ' + data.compliance.percentage + '%');
                })
                .catch(err => {
                    console.error('Error:', err);
                    alert('Error: ' + err.message);
                });
        });
        console.log('✅ Event listener attached!');
    } else {
        console.error('❌ Button not found!');
    }
});
