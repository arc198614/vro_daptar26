<script lang="ts">
  import { onMount } from 'svelte';

  let inspections: any[] = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      const response = await fetch('/api/inspections');
      const data = await response.json();

      if (data.success) {
        inspections = data.inspections;
      } else {
        error = data.error || 'Failed to load inspections';
      }
    } catch (err) {
      error = 'Failed to load inspections';
      console.error('Error loading inspections:', err);
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>डॅशबोर्ड - ग्रा.म.अ. दप्तर तपासणी</title>
</svelte:head>

<div class="container-fluid py-4">
  <div class="row">
    <div class="col-12">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="h3 mb-0">डॅशबोर्ड - ग्रा.म.अ. दप्तर तपासणी</h1>
        <a href="/inspect" class="btn btn-primary">
          <i class="fas fa-plus me-2"></i>नवीन तपासणी
        </a>
      </div>

      {#if loading}
        <div class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3">तपासण्या लोड होत आहेत...</p>
        </div>
      {:else if error}
        <div class="alert alert-danger" role="alert">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {error}
        </div>
      {:else}
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">तपासण्या ({inspections.length})</h5>
          </div>
          <div class="card-body">
            {#if inspections.length === 0}
              <div class="text-center py-5">
                <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">कोणत्याही तपासण्या आढळल्या नाहीत</h5>
                <p class="text-muted">नवीन तपासणी सुरू करण्यासाठी वरच्या बटणावर क्लिक करा.</p>
              </div>
            {:else}
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>सजा</th>
                      <th>ग्राम महसूल अधिकारी</th>
                      <th>रुजू दिनांक</th>
                      <th>तपासणी दिनांक</th>
                      <th>स्थिती</th>
                      <th>कृती</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each inspections as inspection}
                      <tr>
                        <td>
                          <code class="small">{inspection.ID}</code>
                        </td>
                        <td>{inspection.सजा || '-'}</td>
                        <td>{inspection.नाव || '-'}</td>
                        <td>{inspection['रुजू होण्याचा दिनांक'] || '-'}</td>
                        <td>{inspection.तारीख || '-'}</td>
                        <td>
                          <span class="badge bg-{inspection['एकूण ग्रेड'] === 'Pending' ? 'warning' : 'success'}">
                            {inspection['एकूण ग्रेड'] || 'Pending'}
                          </span>
                        </td>
                        <td>
                          <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" title="View Details">
                              <i class="fas fa-eye"></i>
                            </button>
                            {#if inspection['फाईल लिंक']}
                              <a href={inspection['फाईल लिंक']} target="_blank" class="btn btn-outline-info" title="View File">
                                <i class="fas fa-file"></i>
                              </a>
                            {/if}
                            <button class="btn btn-outline-secondary" title="Export PDF">
                              <i class="fas fa-file-pdf"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .table th {
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .badge {
    font-size: 0.75rem;
  }

  .btn-group-sm .btn {
    padding: 0.25rem 0.5rem;
  }
</style>