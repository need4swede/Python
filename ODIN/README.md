<html lang="en">
	<head>
    	<meta charset="UTF-8">
    	<meta http-equiv="X-UA-Compatible" content="IE=edge">
    	<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<script src="https://kit.fontawesome.com/a1382ab6b0.js" crossorigin="anonymous"></script>
		<title>ODIN - Documentation</title>
		<!-- external CSS link -->
		<link rel="stylesheet" href="css/normalize.css">
		<link rel="stylesheet" href="css/style.css">
	</head>
	<body>
		<header>
			<nav class="nav">
				<span class="main-nav-link"><a href="index.html">HOME</a></span>
				<ul class="nav-list">
					<li class="nav-link">INTRODUCTION</li>
					<li class="nav-link">FUNCTIONS</li>
					<li class="nav-link">CONSOLE COMMANDS</li>
					<li class="nav-link">FAQ</li>
				</ul>
				<span class="main-nav-link"><a href="mailto:theneed4swede@gmail.com">CONTACT</a></span>
			</nav> 
		</header>
		<main class="main-title">
			<h1>ODIN</h1>
			<div class="underline"></div>
			<img class="logo" src="doc/img/logo.png" alt="logo.png">
			<h3 class="subtitle">Omniscient Database for Inventory Notation</h3>
			<h5 class="description-title">Always keep an eye on what matters</h5>
			<aside>Python 3.9 / PyQt6 / SQLite3</aside>
		</main>
		<section class="introduction">
			<h2>Introduction</h2>
			<h3 class="subtitle">What is ODIN?</h3>
			<p class="description">ODIN is an asset management system intended [primarily] for I.T. teams of small to medium businesses
				that need a versitile and modular inventory system to manage their equipment, but may not have the resources
				necessary to adopt and pay for expensive alternatives. ODIN was built with modularity in mind, making it easy to 
				change every part of the experience to fit your organization's needs.
			</p>
			<p class="description">Built in Python 3, ODIN uses Qt and SQLite to deliver a fully customizable GUI and saves all of its data into a SQL Database.
				This grants adminstrators the ability to sync their databases across a network and access (and ammend) various database
				entries with ease. Future versions of ODIN will include nodes that
				have network features built in &mdash; but for now, the data is saved locally and will have to be synced manually.
			</p>
		</section>
		<section class="functions">
			<section class="functions data-entry">
				<h2>Functions</h2>
				<h3>Data Entry</h3>
				<h4>ODIN's Default Entries:</h4>
				<p><strong>Site</strong>&mdash; Jobsite / District / Region</p>
				<p><strong>Selection</strong>&mdash; Asset Category</p>
				<p><strong>Make</strong>&mdash; Manufacturer of Asset</p>
				<p><strong>Asset Tag</strong>&mdash; Asset Tag of Asset</p>
				<p><strong>Assigned</strong>&mdash; Who / What the Asset is Assigned to</p>
				<p><strong>Location</strong>&mdash; Location of Asset</p>
				<p><strong>Status</strong>&mdash; Status of the Asset</p>
				<p><strong>Service Tag</strong>&mdash; Serial Number or Service Tag of Asset</p>
				<p><strong>Info</strong>&mdash; Additional Information about Asset</p>
				<p><strong>Date</strong>&mdash; Date of Asset's last change</p>
			</section>
		</section>
		<footer>
		</footer>
	</body>
</html>
