/**
 * JobListing.js
 * 
 * This script handles the job listing functionality.
 */

/** FUNCTION: fetchJobs
 * function fetches the jobs from the Flask server.
 * @returns {array} jobs - The array of jobs to be displayed.
 */
async function fetchJobs(params) {
    const options = { // request options
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }

    // fetch the jobs from the Flask server
    try {
        const response = await fetch('/app_routes/retrieve_jobs', options);

        if (!response.ok) {
            throw new Error('Failed to fetch jobs');
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error('Error fetching jobs:', error);
    }
}


/** FUNCTION: generateJobsList
 * function generates the job listings on the jobs page using the data from the Flask server.
 * @param {string} jobListingContainerId - The ID of the container that contains the job listings.
 * @param {array} jobs - The array of jobs to be displayed.
 */
function generateJobsList(jobListingContainerId, jobs) {
    // remove the loading text
    const loadingText = document.getElementById('loadingText');
    loadingText.remove();
    

    // collect jobs
    const jobsContainer = document.getElementById(jobListingContainerId); // get the container for the job listings

    jobs.forEach(job => {
        
        // Create a job card element
        const jobCard = document.createElement('div');
        jobCard.className = 'card row mb-3 mt-3 ml-0 mr-0';
        jobCard.id = job.id;

        jobCard.innerHTML = `
            <div class="card-header d-flex justify-content-between align-items-center" 
                style="color: #000;"
            >
                <div class="d-flex align-items-center">
                    <p class="lead m-0" style="font-size: 13px;"><b>${formatPay(job.pay)}</b></p>
                    <div class="spacer" style="width: 10px;"></div>
                    <p class="lead m-0" style="font-size: 15px;"><b>⦁</b></p>
                    <div class="spacer" style="width: 10px;"></div>
                    ${job.title}
                    <div class="spacer" style="width: 10px;"></div>
                    <span class="badge bg-${formatOrg(job.company)}">${job.company}</span>
                    <div class="spacer" style="width: 10px;"></div>
                    
                </div>
                <div class="float-end job-actions">
                    <a href="#" class="btn btn-primary btn-sm apply-button">Apply</a>
                    <a href="#" class="btn btn-outline-danger btn-sm reject-button">Reject</a>
                </div>
            </div>

            <div class="card-body">
                <em>
                    <p class="card-text" style="font-size: 12px;">
                        ${formatJobText(job.job_text)}
                    </p>
                </em>
            </div>
        `;

        // Append the job card to the container
        jobsContainer.appendChild(jobCard);

        // Bind the job data to the job-actions div
        const jobActionsDiv = jobCard.querySelector('.job-actions');
        jobActionsDiv.dataset.job = job;

        // add showApplyWindow to apply button
        const jobActions = {
            applyButton: jobCard.querySelector('.apply-button'),
            rejectButton: jobCard.querySelector('.reject-button')
        }
        
        jobActions.applyButton.onclick = () => handleApply(job); // show apply window
        jobActions.rejectButton.onclick = () => handleReject(job); // show reject window
    })
}


/** COMPONENT: Application Handlers
 * function opens the apply window for a job.
 */
function handleApply(job) {

    // get modal template
    const modal = document.getElementById('applicationsModal');
    const modal_content_root = modal.querySelector('.modal-content');

    // Define the modal content
    modal_content_root.innerHTML = `
        <div class="modal-header">
            <h5 class="modal-title">Apply for:<br>${job.title}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body">
            <div class="mb-3">
                <label for="exampleFormControlTextarea1" class="form-label">Application Statement:</label>
                <textarea class="form-control" id="exampleFormControlTextarea1" rows="10" placeholder="Generating application statement..."></textarea>
            </div>
        </div>

        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary">Apply</button>
        </div>
    `;

    // handle apply actions

    // initialize the modal
    const applyModal = new bootstrap.Modal(modal);
    applyModal.show();


    // send a request to generate an application statement for the job
}

function handleReject(job) {
    console.log("Rejecting job");

    //send rejection request to the server

    //remove job from the list
    const jobCard = document.getElementById(job.id);
    jobCard.remove();
}


/**
 * FORMATTING FUNCTIONS
 */
function formatOrg(company) {
    return company.replaceAll(' ', '');
}

function formatJobText(jobText) {
    let formattedText = jobText
        .replace(/\n/g, '<br>')

    return formattedText;
}

function formatPay(pay) {
    
    //hourly jobs
    if (pay <= 50) {
        return `£${pay}/hour`;
    }

    else if (pay <= 1000) {
        return `£${pay}/day`;
    }

    else {
        return `£${pay}`
    }
}

