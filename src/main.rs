use anyhow::{Error, Result};
use clap::{Parser, Subcommand};
use std::sync::Arc;

#[derive(Debug, Parser)]
#[command(name = "indexify")]
#[command(about = "CLI for the Indexify Server", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Debug, Subcommand)]
enum Commands {
    #[command(about = "Start the server")]
    Start {
        #[arg(short, long)]
        config_path: String,
    },
    InitConfig {
        config_path: String,
    },
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing_subscriber::fmt::init();
    let args = Cli::parse();
    match args.command {
        Commands::Start { config_path } => {
            let config = indexify::ServerConfig::from_path(config_path)?;
            let server = indexify::Server::new(Arc::new(config))?;
            server.run().await?
        }
        Commands::InitConfig { config_path } => {
            println!("Initializing config file at: {}", &config_path);
            indexify::ServerConfig::generate(config_path).unwrap();
        }
    }
    Ok(())
}