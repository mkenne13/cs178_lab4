// Define margins and dimensions for the bar chart
const margin = { top: 30, right: 30, bottom: 70, left: 80 };
const width = 800 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

// Create the SVG container for the bar chart
const svg_bar = d3.select("#plot-container")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Function to update filter options
function update_filter_options(group_filters) {
    for (const group in group_filters) {
        const filterSelect = document.getElementById(`${group}-filter`);
        filterSelect.innerHTML = '<option value="all">All</option>';
        group_filters[group].forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            filterSelect.appendChild(option);
        });
    }
}

// Function to draw the bar chart
function draw_bar(data, x_column, y_column) {
    svg_bar.selectAll("*").remove();
    
    const xScale = d3.scaleBand()
        .domain(data.map(d => d.name))
        .range([0, width])
        .padding(0.4);
    
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)])
        .range([height, 0]);
    
    svg_bar.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => xScale(d.name))
        .attr("y", d => yScale(d.value))
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - yScale(d.value))
        .attr("fill", "lightblue");
    
    svg_bar.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(xScale))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");
    
    svg_bar.append("g").call(d3.axisLeft(yScale));
    
    // Add x-axis label
    svg_bar.append("text")
        .attr("class", "axis-label")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom - 10)
        .style("text-anchor", "middle")
        .text(x_column);
    
    // Add y-axis label
    svg_bar.append("text")
        .attr("class", "axis-label")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("y", -margin.left + 20)
        .style("text-anchor", "middle")
        .text(y_column);
}

// Function to update the aggregate
function update_aggregate(value, key) {
    fetch('/update_aggregate', {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ value, key }),
        headers: { 'content-type': 'application/json' }
    }).then(async response => {
        const results = await response.json();
        draw_bar(results.data, results.x_column, results.y_column);
    });
}

// Function to update the filter
function update_filter(value, key) {
    fetch('/update_filter', {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ value, key }),
        headers: { 'content-type': 'application/json' }
    }).then(async response => {
        const results = await response.json();
        draw_bar(results.data, results.x_column, results.y_column);
        update_filter_options(results.group_filters);
    });
}

// Initial call to draw the bar chart
update_aggregate(null, null);