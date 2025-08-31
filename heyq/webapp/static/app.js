(function(){
  const micBtn = document.getElementById('micBtn');
  const cancelBtn = document.getElementById('cancelBtn');
  const clearBtn = document.getElementById('clearBtn');
  const runBtn = document.getElementById('runBtn');
  const productEl = document.getElementById('product');
  const headedEl = document.getElementById('headed');
  const useAIEl = document.getElementById('useAI');
  const statusEl = document.getElementById('status');
  const speedEl = document.getElementById('speed');
  const transcriptWrap = document.getElementById('transcript');
  const heardEl = document.getElementById('heard');
  const verificationEl = document.getElementById('verification');
  const verificationDetailsEl = document.getElementById('verification-details');

  function setStatus(msg){ statusEl.textContent = msg || ''; }
  function toggleRun(){ 
    const inputText = productEl.value.trim();
    const heardText = (heardEl.textContent || heardEl.innerText || '').trim();
    const hasText = inputText.length > 0 || heardText.length > 0;
    runBtn.disabled = !hasText;
    console.log('🔘 toggleRun check:', {inputText, heardText, hasText, disabled: runBtn.disabled});
  }

  function showVerification(verification) {
    if (!verification) {
      verificationEl.classList.add('hidden');
      return;
    }

    let html = '';
    
    // Show AI enhancement indicator
    if (verification.ai_enhanced) {
      html += `<div class="verification-item verification-info" style="font-weight: bold; margin-bottom: 12px; background: rgba(37, 99, 235, 0.05);">
        <span class="verification-icon">🤖</span>
        <span class="verification-text">AI-ENHANCED AUTOMATION</span>
      </div>`;
    }
    
    // Show overall test status at the top
    if (verification.test_status === 'PASS') {
      html += `<div class="verification-item verification-pass" style="font-weight: bold; margin-bottom: 12px;">
        <span class="verification-icon">✅</span>
        <span class="verification-text">TEST PASSED</span>
      </div>`;
    } else if (verification.test_status === 'FAIL') {
      html += `<div class="verification-item verification-fail" style="font-weight: bold; margin-bottom: 12px;">
        <span class="verification-icon">❌</span>
        <span class="verification-text">TEST FAILED</span>
      </div>`;
    } else if (verification.test_status === 'PARTIAL') {
      html += `<div class="verification-item verification-info" style="font-weight: bold; margin-bottom: 12px;">
        <span class="verification-icon">⚠️</span>
        <span class="verification-text">PARTIAL SUCCESS</span>
      </div>`;
    }
    
    // Show action-specific details
    if (verification.action) {
      const actionMessages = {
        'navigate': 'Website navigation completed',
        'login_only': 'Login authentication completed', 
        'add_to_cart_flow': 'Product added to cart',
        'add_to_cart': 'Product added to cart',
        'full_checkout_flow': 'Complete order flow executed',
        'checkout': 'Checkout process completed'
      };
      const actionMsg = actionMessages[verification.action] || verification.action;
      html += `<div class="verification-item verification-info">
        <span class="verification-icon">🔄</span>
        <span class="verification-text">Action: <strong>${actionMsg}</strong></span>
      </div>`;
    }
    
    if (verification.product_verification === true) {
      html += `<div class="verification-item verification-pass">
        <span class="verification-icon">✅</span>
        <span class="verification-text">Product found: <strong>${verification.product_name}</strong></span>
      </div>`;
    } else if (verification.product_verification === false) {
      html += `<div class="verification-item verification-fail">
        <span class="verification-icon">❌</span>
        <span class="verification-text">Product not found: <strong>${verification.product_name}</strong></span>
      </div>`;
    }

    if (verification.price_verification === true) {
      html += `<div class="verification-item verification-pass">
        <span class="verification-icon">✅</span>
        <span class="verification-text">Price match: Expected <strong>${verification.expected_price}</strong>, Got <strong>${verification.actual_price}</strong></span>
      </div>`;
    } else if (verification.price_verification === false) {
      html += `<div class="verification-item verification-fail">
        <span class="verification-icon">❌</span>
        <span class="verification-text">Price mismatch: Expected <strong>${verification.expected_price}</strong>, Got <strong>${verification.actual_price}</strong></span>
      </div>`;
    } else if (verification.price_verification === null && verification.actual_price) {
      html += `<div class="verification-item verification-info">
        <span class="verification-icon">ℹ️</span>
        <span class="verification-text">Price found: <strong>${verification.actual_price}</strong> (no expected price set)</span>
      </div>`;
    }

    verificationDetailsEl.innerHTML = html;
    verificationEl.classList.remove('hidden');
  }

  async function runFlow(){
    console.log('🚀 Run button clicked!');
    console.log('🚀 Input field value:', productEl.value);
    console.log('🚀 Heard element text:', heardEl.textContent);
    console.log('🚀 Run button disabled?', runBtn.disabled);
    console.log('🤖 AI Enhanced:', useAIEl.checked);
    
    let text = productEl.value.trim();
    if(!text){
      // Try to get clean text from heard element
      const heardText = heardEl.textContent || heardEl.innerText || '';
      if(heardText.trim()) {
        text = heardText.trim();
        productEl.value = text; // Ensure input field has the text
        console.log('🚀 Using heard text:', text);
      }
    }
    if(!text){ 
      console.log('❌ No text found to run');
      setStatus('Please say or type a flow or product first.'); 
      return; 
    }
    
    console.log('🚀 Running with text:', text);
    
    const headed = headedEl.checked;
    const useAI = useAIEl.checked;
    const aiIndicator = useAI ? ' 🤖' : '';
    setStatus(`Running: ${text}${aiIndicator} ${headed ? '(showing browser)' : ''}`);
    verificationEl.classList.add('hidden');
    const prev = runBtn.textContent; runBtn.textContent = 'Running…'; runBtn.disabled = true;
    try{
      // Send the raw utterance to NLP system with AI flag
      const utterance = text;
      const slow_mo = parseInt(speedEl.value, 10) || 0;
      const use_ai = useAI;
      const res = await fetch(`${window.location.origin}/api/run`,{
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({utterance, headed, slow_mo, use_ai})
      });
      let data = null; let textOut = '';
      try { data = await res.json(); } catch(_) { textOut = await res.text(); }
      if(res.ok && data && data.ok){
        showVerification(data.verification);
        
        // Show user-friendly message if available
        if(data.verification && data.verification.user_message) {
          setStatus(`✅ ${data.verification.user_message}`);
        } else if(data.verification && data.verification.message) {
          setStatus(data.verification.message);
        } else if(data.site || data.intent){
          const i = data.intent || {};
          const parts = [];
          if(data.site) parts.push(`site=${data.site}`);
          if(i.action) parts.push(`action=${i.action}`);
          if(i.item) parts.push(`item=${i.item}`);
          if(i.qty) parts.push(`qty=${i.qty}`);
          setStatus(`Done (${parts.join(', ')})`);
        } else {
          setStatus('Done.');
        }
      }
      else {
        const msg = (data && (data.error || data.message)) || textOut || `HTTP ${res.status}`;
        setStatus(`Error: ${msg}`);
      }
    } catch(err){ setStatus('Network error.'); }
    finally { runBtn.textContent = prev; toggleRun(); }
  }

  productEl.addEventListener('input', toggleRun);
  productEl.addEventListener('keydown', (e)=>{
    if(e.key === 'Enter'){
      e.preventDefault();
      runFlow();
    }
  });
  runBtn.addEventListener('click', runFlow);

  // Clear button functionality
  function clearPrompt() {
    productEl.value = '';
    heardEl.textContent = '';
    commandBuffer = '';
    finalCompleteCommand = '';
    allTranscribedText = '';
    transcriptWrap.classList.add('hidden');
    verificationEl.classList.add('hidden');
    setStatus('');
    toggleRun();
  }

  clearBtn.addEventListener('click', clearPrompt);

  // Voice Recognition Variables - CONTINUOUS VERSION FOR FULL SENTENCES
  let recognizing = false; 
  let recognition = null; 
  let finalTranscript = '';
  let isMicActive = false;
  
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(SR){
    recognition = new SR();
    recognition.lang = 'en-US'; 
    recognition.continuous = true;  // Back to true for full sentences
    recognition.interimResults = true;
    
    recognition.onresult = (e)=>{
      let interimTranscript = '';
      let newFinalTranscript = '';
      
      // Process all results from the current recognition session
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const transcript = e.results[i][0].transcript;
        if (e.results[i].isFinal) {
          newFinalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }
      
      // Apply corrections
      const finalCorrected = correctSTTErrors(newFinalTranscript);
      const interimCorrected = correctSTTErrors(interimTranscript);
      
      // Accumulate final results to build complete sentence
      if (finalCorrected) {
        finalTranscript += ' ' + finalCorrected;
        finalTranscript = finalTranscript.trim();
        console.log('📝 Updated finalTranscript:', finalTranscript);
      }
      
      // Show complete sentence with current interim text
      const displayText = finalTranscript + (interimCorrected ? ' ' + interimCorrected : '');
      if (displayText.trim()) {
        heardEl.innerHTML = `<span style="color: #2563eb; font-weight: 500;">${finalTranscript}</span><span style="color: #888; font-style: italic;">${interimCorrected ? ' ' + interimCorrected : ''}</span>`;
        heardEl.setAttribute('data-text', finalTranscript); // Store clean final text
        transcriptWrap.classList.remove('hidden');
        console.log('📝 Updated heard display with:', displayText);
        console.log('📝 Stored data-text:', finalTranscript);
      }
      
      console.log('🎤 Speech result:', {newFinal: finalCorrected, interim: interimCorrected, completeSentence: finalTranscript});
    };
    
    function correctSTTErrors(text) {
      const corrections = {
        'backpart': 'backpack', 'back part': 'backpack', 'backback': 'backpack',
        'cut': 'cart', 'card': 'cart', 'curt': 'cart', 'court': 'cart',
        'bless': 'place', 'bliss': 'place', 'blessed': 'place',
        'sauce demo': 'saucedemo', 'source demo': 'saucedemo',
        'check out': 'checkout', 'at a': 'add a', 'at the': 'add the'
      };
      
      let corrected = text;
      const sortedCorrections = Object.entries(corrections)
        .sort(([a], [b]) => b.length - a.length);
      
      for (const [wrong, right] of sortedCorrections) {
        const regex = new RegExp(`\\b${wrong.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
        corrected = corrected.replace(regex, right);
      }
      
      return corrected;
    }

    recognition.onerror = (e)=>{
      if(e.error === 'not-allowed' || e.error === 'service-not-allowed'){
        setStatus('❌ Microphone permission denied');
        micBtn.disabled = true;
      } else {
        setStatus('❌ Mic error: ' + e.error);
      }
      recognizing = false;
      updateMicButton();
    };

    recognition.onstart = ()=> { 
      recognizing = true;
      updateMicButton();
      setStatus('🎤 Listening... speak clearly');
      finalTranscript = ''; // Reset for new session
    };

    recognition.onend = ()=> {
      recognizing = false; 
      updateMicButton();
      
      if (isMicActive) {
        // If user is still recording, restart
        setTimeout(() => {
          if (isMicActive && !recognizing) {
            tryStartListening();
          }
        }, 100);
      } else {
        setStatus('🎤 Click microphone to start voice capture');
      }
    };
  } else {
    micBtn.disabled = true; 
    setStatus('❌ Web Speech API not supported');
  }

  function updateMicButton() {
    if (recognizing) {
      micBtn.textContent = '🔴';
      micBtn.style.backgroundColor = '#ff4444';
      micBtn.style.color = 'white';
      micBtn.style.border = '2px solid #ff6666';
    } else {
      micBtn.textContent = '🎙️';
      micBtn.style.backgroundColor = isMicActive ? '#4CAF50' : '#f0f0f0';
      micBtn.style.color = isMicActive ? 'white' : '#333';
      micBtn.style.border = isMicActive ? '2px solid #66bb6a' : '2px solid #ddd';
    }
  }

  async function requestMicPermission(){
    // Check if we're on HTTPS or localhost (required for microphone)
    const isSecureContext = location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
    
    if (!isSecureContext) {
      setStatus('❌ Microphone requires HTTPS or localhost. Try typing commands instead.');
      return false;
    }
    
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
      try { 
        await navigator.mediaDevices.getUserMedia({audio:true}); 
        setStatus('✅ Microphone permission granted');
        return true;
      }
      catch(err) { 
        console.warn('Microphone permission denied:', err);
        setStatus('❌ Microphone permission denied. You can still type commands!');
        return false;
      }
    } else {
      setStatus('❌ Microphone not supported. You can still type commands!');
      return false;
    }
  }

  function tryStartListening(){
    if(!recognition || recognizing) return;
    try { 
      recognition.start(); 
      recognizing = true; 
      updateMicButton();
    }
    catch(_) { 
      console.log('Recognition start failed - may already be running');
    }
  }

  // Manual microphone control event listener - CONTINUOUS SENTENCE VERSION
  micBtn.addEventListener('click', ()=>{
    console.log('🎤 Microphone button clicked!', {isMicActive, recognizing});
    
    if(!recognition) {
      setStatus('❌ Speech recognition not available in this browser');
      return;
    }
    
    if(!isMicActive) {
      // Start listening
      console.log('▶️ Starting microphone for continuous speech...');
      isMicActive = true;
      finalTranscript = ''; // Reset for new session
      heardEl.textContent = '';
      tryStartListening();
      setStatus('🎤 Microphone activated - speak your complete sentence');
    } else {
      // Stop listening and capture complete sentence
      console.log('⏹️ Stopping microphone...');
      isMicActive = false;
      
      if(recognizing) {
        recognition.stop(); 
      }
      recognizing = false; 
      updateMicButton();
      
      // Get the complete transcribed sentence from multiple sources - COMPREHENSIVE FALLBACK
      const completeSentence = finalTranscript.trim();
      const heardDisplayText = (heardEl.textContent || heardEl.innerText || '').trim();
      const heardDataText = heardEl.getAttribute('data-text') || '';
      
      // Try multiple sources in order of preference
      let bestText = completeSentence || heardDisplayText || heardDataText;
      
      // If still empty, try to extract from the HTML content
      if (!bestText && heardEl.innerHTML) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = heardEl.innerHTML;
        bestText = (tempDiv.textContent || tempDiv.innerText || '').trim();
      }
      
      console.log('📝 DEBUG Voice Stop - ALL SOURCES:');
      console.log('  - finalTranscript:', finalTranscript);
      console.log('  - heardEl.textContent:', heardEl.textContent);
      console.log('  - heardEl.innerText:', heardEl.innerText);
      console.log('  - heardEl.getAttribute("data-text"):', heardDataText);
      console.log('  - heardEl.innerHTML:', heardEl.innerHTML);
      console.log('  - FINAL bestText chosen:', bestText);
      console.log('  - Current input field value:', productEl.value);
      
      if(bestText) {
        // Clean up wake words and extra spaces
        const wake = /(hey\s*q|heyq|hey\s*queue|hey\s*buddy)/i;
        const cleanText = bestText.replace(wake, '').trim();
        const displayText = cleanText || bestText;
        
        console.log('📝 SETTING INPUT FIELD TO:', displayText);
        
        // FORCE replace placeholder text in input field with captured sentence
        productEl.value = displayText;
        productEl.setAttribute('value', displayText); // Force attribute update
        
        // Clear placeholder attribute if it exists
        if (productEl.hasAttribute('placeholder')) {
          const originalPlaceholder = productEl.getAttribute('placeholder');
          productEl.removeAttribute('placeholder');
          setTimeout(() => {
            if (!productEl.value) {
              productEl.setAttribute('placeholder', originalPlaceholder);
            }
          }, 100);
        }
        
        // Force focus and selection to make it visible
        productEl.focus();
        productEl.select();
        
        // Trigger multiple events to ensure UI updates
        productEl.dispatchEvent(new Event('input', { bubbles: true }));
        productEl.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Force enable run button
        runBtn.disabled = false;
        toggleRun();
        
        setStatus(`📝 Captured: "${displayText}" - Press Run to execute`);
        
        console.log('📝 Input field value after update:', productEl.value);
        console.log('📝 Input field element:', productEl);
        
        // Keep heard text visible with proper formatting
        heardEl.innerHTML = `<span style="color: #2563eb; font-weight: 500;">${displayText}</span>`;
        heardEl.setAttribute('data-text', displayText);
        transcriptWrap.classList.remove('hidden');
        
        console.log('✅ VERIFICATION - Input field after all updates:');
        console.log('  - productEl.value:', productEl.value);
        console.log('  - productEl.getAttribute("value"):', productEl.getAttribute('value'));
        console.log('  - Run button disabled?', runBtn.disabled);
        console.log('  - Run button text:', runBtn.textContent);
        
        // Final verification that text is actually there
        setTimeout(() => {
          console.log('🔍 FINAL CHECK (after 500ms):');
          console.log('  - Input field value:', productEl.value);
          console.log('  - Run button disabled:', runBtn.disabled);
          if (!productEl.value) {
            console.error('❌ CRITICAL: Input field is still empty after voice capture!');
            // Emergency fallback - try to set it again
            productEl.value = displayText;
            runBtn.disabled = false;
          }
        }, 500);
      } else {
        setStatus('🎤 No speech detected - try again');
        heardEl.textContent = '';
        transcriptWrap.classList.add('hidden');
      }
    }
  });

  // Cancel button
  cancelBtn.addEventListener('click', ()=>{
    setStatus('🚫 Voice command cancelled');
    heardEl.textContent = '';
    productEl.value = '';
    toggleRun();
    if(recognizing) {
      recognition.stop();
    }
    isMicActive = false;
    recognizing = false;
    updateMicButton();
  });

  // Initialize everything
  console.log('🚀 Initializing voice interface...');
  productEl.value = '';
  toggleRun(); 
  setStatus('🎤 Click microphone to capture voice, then press Run');
  transcriptWrap.classList.add('hidden'); 
  heardEl.textContent = '';
  verificationEl.classList.add('hidden');
  cancelBtn.classList.add('hidden');
  isMicActive = false;
  recognizing = false;
  updateMicButton();
  
  // SDET TESTING FUNCTION - Verify all flows work
  window.testAllFlows = function() {
    console.log('🧪 SDET Testing All Flows:');
    
    // Test 1: Manual text input
    console.log('Test 1: Manual text input');
    productEl.value = 'test manual input';
    toggleRun();
    console.log('  - Input field value:', productEl.value);
    console.log('  - Run button disabled:', runBtn.disabled);
    
    // Test 2: Clear function
    console.log('Test 2: Clear function');
    clearPrompt();
    console.log('  - Input field after clear:', productEl.value);
    console.log('  - Run button disabled after clear:', runBtn.disabled);
    
    // Test 3: Simulate voice capture
    console.log('Test 3: Simulate voice capture');
    heardEl.innerHTML = '<span style="color: #2563eb;">go to saucedemo.com</span>';
    heardEl.setAttribute('data-text', 'go to saucedemo.com');
    console.log('  - Heard element set up with test text');
    
    console.log('🧪 Manual test required: Use microphone and verify input field gets populated');
  };
  
  console.log('🧪 SDET: Type testAllFlows() in console to run tests');
  
  // Request microphone permission
  (async()=>{ 
    await requestMicPermission(); 
    console.log('🎤 Microphone permission requested');
  })();
})();
