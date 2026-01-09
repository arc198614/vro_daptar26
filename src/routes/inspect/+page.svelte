<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let questions: any[] = [];
  let loading = true;
  let submitting = false;
  let submitMessage = '';
  let submitError = '';

  // Form data
  let sajaName = '';
  let vroName = '';
  let registrationDate = '';
  let answers: { [key: string]: string } = {};
  let remarks: { [key: string]: string } = {};
  let files: { [key: string]: File | null } = {};

  onMount(async () => {
    try {
      // For now, use fallback questions since we don't have the API for questions yet
      questions = [
        { "ID": "1", "विभाग": "सामान्य", "प्रश्न": "दप्तर अद्ययावत आहे का?", "अपलोड आवश्यक": "हो" },
        { "ID": "2", "विभाग": "सामान्य", "प्रश्न": "नोंदवही पूर्ण आहे का?", "अपलोड आवश्यक": "नाही" },
        { "ID": "3", "विभाग": "सामान्य", "प्रश्न": "दस्तऐवज व्यवस्थित आहेत का?", "अपलोड आवश्यक": "हो" }
      ];
    } catch (error) {
      console.error('Error loading questions:', error);
    } finally {
      loading = false;
    }
  });

  async function handleSubmit() {
    if (!sajaName || !vroName || !registrationDate) {
      submitError = 'कृपया सर्व आवश्यक माहिती भरा.';
      return;
    }

    submitting = true;
    submitError = '';
    submitMessage = '';

    try {
      const formData = new FormData();

      // Add basic form data
      formData.append('saja_name', sajaName);
      formData.append('vro_name', vroName);
      formData.append('registration_date', registrationDate);

      // Add answers and remarks
      questions.forEach(q => {
        const qId = q.ID;
        formData.append(`q_${qId}`, answers[qId] || '');
        formData.append(`remark_${qId}`, remarks[qId] || '');

        // Add file if exists
        if (files[`file_${qId}`]) {
          formData.append(`file_${qId}`, files[`file_${qId}`]!);
        }
      });

      const response = await fetch('/api/inspect', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (result.success) {
        submitMessage = result.message;
        // Reset form
        sajaName = '';
        vroName = '';
        registrationDate = '';
        answers = {};
        remarks = {};
        files = {};

        // Redirect to dashboard after short delay
        setTimeout(() => {
          goto('/');
        }, 2000);
      } else {
        submitError = result.error || 'तपासणी जतन करण्यात अयशस्वी.';
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      submitError = 'नेटवर्क त्रुटी. कृपया पुन्हा प्रयत्न करा.';
    } finally {
      submitting = false;
    }
  }

  function handleFileChange(event: Event, questionId: string) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0] || null;
    files[`file_${questionId}`] = file;
  }
</script>

<svelte:head>
  <title>नवीन तपासणी - ग्रा.म.अ. दप्तर तपासणी</title>
</svelte:head>

<div class="container-fluid py-4">
  <div class="row justify-content-center">
    <div class="col-lg-8">
      <div class="card shadow">
        <div class="card-header bg-primary text-white">
          <h3 class="card-title mb-0">
            <i class="fas fa-clipboard-list me-2"></i>
            दप्तर तपासणी प्रश्नावली
          </h3>
        </div>
        <div class="card-body">
          {#if loading}
            <div class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-3">प्रश्न लोड होत आहेत...</p>
            </div>
          {:else}
            <form on:submit|preventDefault={handleSubmit}>
              <!-- Administrative Details -->
              <div class="row mb-4">
                <div class="col-md-6 mb-3">
                  <label for="sajaName" class="form-label fw-bold">
                    सजाचे नाव (Saja Name) <span class="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    class="form-control"
                    id="sajaName"
                    bind:value={sajaName}
                    required
                    placeholder="सजाचे नाव प्रविष्ट करा"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="vroName" class="form-label fw-bold">
                    ग्राम महसूल अधिकारी (VRO Name) <span class="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    class="form-control"
                    id="vroName"
                    bind:value={vroName}
                    required
                    placeholder="ग्राम महसूल अधिकारीचे नाव प्रविष्ट करा"
                  >
                </div>
              </div>

              <div class="row mb-4">
                <div class="col-md-6 mb-3">
                  <label for="registrationDate" class="form-label fw-bold">
                    सज्यावर रुजू होण्याचा दिनांक (Saja Registration Date) <span class="text-danger">*</span>
                  </label>
                  <input
                    type="date"
                    class="form-control"
                    id="registrationDate"
                    bind:value={registrationDate}
                    required
                    placeholder="सज्यावर नोंदणी दिनांक निवडा"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="inspectionDate" class="form-label fw-bold">
                    तपासणी दिनांक (Inspection Date) <span class="text-danger">*</span>
                  </label>
                  <input
                    type="date"
                    class="form-control"
                    id="inspectionDate"
                    value={new Date().toISOString().split('T')[0]}
                    readonly
                    title="आजची तारीख आपोआप भरली जाईल"
                  >
                  <small class="form-text text-muted">आजची तारीख आपोआप घेतली जाते</small>
                </div>
              </div>

              <hr class="my-4">

              <!-- Dynamic Questions -->
              {#each questions as question, index}
                <div class="card mb-4 border-left-primary">
                  <div class="card-body">
                    <h5 class="card-title text-primary mb-3">
                      {index + 1}. {question.प्रश्न}
                    </h5>

                    <!-- Radio button options -->
                    <div class="mb-3">
                      <div class="row g-2">
                        <div class="col-auto">
                          <div class="form-check">
                            <input
                              class="form-check-input"
                              type="radio"
                              id="q_{question.ID}_yes"
                              bind:group={answers[question.ID]}
                              value="हो"
                            >
                            <label class="form-check-label" for="q_{question.ID}_yes">
                              हो
                            </label>
                          </div>
                        </div>
                        <div class="col-auto">
                          <div class="form-check">
                            <input
                              class="form-check-input"
                              type="radio"
                              id="q_{question.ID}_no"
                              bind:group={answers[question.ID]}
                              value="नाही"
                            >
                            <label class="form-check-label" for="q_{question.ID}_no">
                              नाही
                            </label>
                          </div>
                        </div>
                        <div class="col-auto">
                          <div class="form-check">
                            <input
                              class="form-check-input"
                              type="radio"
                              id="q_{question.ID}_na"
                              bind:group={answers[question.ID]}
                              value="निरंक/लागू नाही"
                            >
                            <label class="form-check-label" for="q_{question.ID}_na">
                              निरंक/लागू नाही
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- File Upload (if required) -->
                    {#if question['अपलोड आवश्यक'] === 'हो'}
                      <div class="mb-3">
                        <label for="file_{question.ID}" class="form-label text-secondary">
                          <i class="fas fa-paperclip me-1"></i>
                          दस्तऐवज अपलोड करा (Upload File)
                        </label>
                        <input
                          class="form-control"
                          type="file"
                          id="file_{question.ID}"
                          on:change={(e) => handleFileChange(e, question.ID)}
                          accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                        >
                        {#if files[`file_${question.ID}`]}
                          <small class="text-success mt-1 d-block">
                            <i class="fas fa-check-circle me-1"></i>
                            {files[`file_${question.ID}`]?.name} ({(files[`file_${question.ID}`]?.size || 0) / 1024} KB)
                          </small>
                        {/if}
                      </div>
                    {/if}

                    <!-- Remarks -->
                    <div class="mb-3">
                      <label for="remark_{question.ID}" class="form-label text-secondary">
                        <i class="fas fa-comment me-1"></i>
                        अधिकारी शेरा (Remarks)
                      </label>
                      <textarea
                        class="form-control"
                        id="remark_{question.ID}"
                        rows="2"
                        bind:value={remarks[question.ID]}
                        placeholder="शेरा प्रविष्ट करा..."
                      ></textarea>
                    </div>
                  </div>
                </div>
              {/each}

              <!-- Submit Button -->
              <div class="d-grid mt-4">
                <button
                  type="submit"
                  class="btn btn-primary btn-lg"
                  disabled={submitting}
                >
                  {#if submitting}
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    जतन होत आहे...
                  {:else}
                    <i class="fas fa-save me-2"></i>
                    जतन करा (Save Inspection)
                  {/if}
                </button>
              </div>

              <!-- Messages -->
              {#if submitMessage}
                <div class="alert alert-success mt-3" role="alert">
                  <i class="fas fa-check-circle me-2"></i>
                  {submitMessage}
                </div>
              {/if}

              {#if submitError}
                <div class="alert alert-danger mt-3" role="alert">
                  <i class="fas fa-exclamation-triangle me-2"></i>
                  {submitError}
                </div>
              {/if}
            </form>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .border-left-primary {
    border-left: 4px solid #007bff !important;
  }

  .card-title {
    color: #007bff !important;
  }

  .form-check-input:checked {
    background-color: #007bff;
    border-color: #007bff;
  }

  .btn:disabled {
    opacity: 0.6;
  }
</style>