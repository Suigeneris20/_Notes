def close_session(db_name, session_id, deallocate=True):
    """Close session and archive to history"""
    conn = get_connection()
    
    # Get session details before closing
    cursor = conn.execute(
        """
        SELECT user_id, grid, application, slots_allocated, created_at
        FROM sessions WHERE session_id = ?
        """,
        (session_id,)
    )
    session_data = cursor.fetchone()
    
    if not session_data:
        return False
    
    # Archive to closed_sessions
    closed_at = datetime.now()
    duration = (closed_at - session_data[4]).total_seconds()
    
    conn.execute(
        """
        INSERT INTO closed_sessions 
        (original_session_id, user_id, grid, application, slots_allocated,
         created_at, closed_at, duration_seconds, close_reason, closed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (session_id, *session_data, closed_at, duration, "manual", "user")
    )
    
    # Deallocate slots if requested
    if deallocate:
        # Your deallocation logic
        pass
    
    # Remove from active sessions
    conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    
    conn.commit()
    conn.close()
    return True
