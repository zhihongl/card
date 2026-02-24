# AGENTS.md

## Cursor Cloud specific instructions

This is a Java/Maven CLI application (Credit Card Fraud Detector). No external services, databases, or Docker are required.

### Prerequisites

- **JDK 8+** (OpenJDK 21 is pre-installed in the cloud environment)
- **Maven 3.x** (installed via `sudo apt-get install -y maven`)

### Common commands

See `README.md` for project overview. Key commands:

| Action | Command |
|--------|---------|
| Run tests | `mvn clean test` |
| Build JAR | `mvn clean package` |
| Run app | `java -cp target/card-1.0-SNAPSHOT.jar au.com.zlu.App <file_path> <threshold>` |

### Notes

- The `pom.xml` declares source/target 1.7 in properties but the compiler plugin overrides to Java 8. JDK 21 handles this via `--release`/cross-compilation.
- The last test in `AppTest.java` (large transaction test) is commented out intentionally — it causes `OutOfMemoryError` by design.
- There is no linter configured beyond the Maven compiler checks. `mvn clean test` is the primary validation command.
- The sample input file is `transactions_file` at the repository root.
